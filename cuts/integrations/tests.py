from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from adminprofile.models import CustomUser
from unittest.mock import patch, MagicMock
import json

class StripeIntegrationTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_success(self, mock_create):
        mock_create.return_value = MagicMock(url="https://stripe.com/checkout/session_id")
        
        response = self.client.get(reverse("stripe_checkout"))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'url': 'https://stripe.com/checkout/session_id'})
        mock_create.assert_called_once()

    def test_create_checkout_session_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("stripe_checkout"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Authentication required"})

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_success(self, mock_construct):
        # Mock a successful payment event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': self.user.id,
                    'customer': 'cus_test_123'
                }
            }
        }
        mock_construct.return_value = mock_event
        
        # Use content_type='text/plain' to avoid multipart encoding
        response = self.client.post(
            reverse("stripe_webhook"),
            data="fake_payload",
            content_type="text/plain",
            HTTP_STRIPE_SIGNATURE="fake_sig"
        )
        
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_platform_paid)
        self.assertEqual(self.user.stripe_customer_id, 'cus_test_123')

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct):
        import stripe
        # SignatureVerificationError needs sig_header as first arg
        mock_construct.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "fake_sig")
        
        response = self.client.post(
            reverse("stripe_webhook"),
            data="fake_payload",
            content_type="text/plain",
            HTTP_STRIPE_SIGNATURE="fake_sig"
        )
        
        self.assertEqual(response.status_code, 400)
