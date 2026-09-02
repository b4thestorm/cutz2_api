import json

from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch
from langchain_core.messages import AIMessage
from chat.models import CalendarAgent
from langgraph.constants import END
from adminprofile.models import CustomUser


class BarberAgentEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.barber = CustomUser.objects.create_user(
            username="barber1",
            email="barber1@example.com",
            password="irrelevant",
            title="Mr.",
            description="Test barber",
            twilio_phone_number="+15555550100",
        )
        cls.barber.role = CustomUser.Role.BARBER
        cls.barber.save()

        cls.client_user = CustomUser.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="irrelevant",
            title="Mx.",
            description="Test client",
            role=CustomUser.Role.CLIENT,
            twilio_phone_number="+15555550100",
        )
        cls.client_user.role = CustomUser.Role.CLIENT
        cls.client_user.save()

    def test_post_returns_barber_for_known_phone_number(self):
        response = self.client.post(
            reverse("barber_agent"),
            data=json.dumps({"twilio_phone_number": "+15555550100"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["email"], "barber1@example.com")
        self.assertEqual(body["twilio_phone_number"], "+15555550100")
        self.assertEqual(body["barber_id"], self.barber.id)

    def test_post_returns_404_for_unknown_phone_number(self):
        response = self.client.post(
            reverse("barber_agent"),
            data=json.dumps({"twilio_phone_number": "+15555550999"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_returns_400_when_field_missing(self):
        response = self.client.post(
            reverse("barber_agent"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_returns_400_for_invalid_json(self):
        response = self.client.post(
            reverse("barber_agent"),
            data="not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_get_method_not_allowed(self):
        response = self.client.get(reverse("barber_agent"))
        self.assertEqual(response.status_code, 405)

    def test_does_not_match_client_with_same_phone_number(self):
        response = self.client.post(
            reverse("barber_agent"),
            data=json.dumps({"twilio_phone_number": "+15555550100"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "barber1@example.com")


class CalendarAgentToolTests(TestCase):
    def test_book_appointment_calls_integration(self):
        agent = CalendarAgent()
        with patch('integrations.models.GCalIntegration.insert_service_event') as mock_insert:
            result = agent.book_appointment.func(agent, {})
            self.assertIn('messages', result)
            self.assertIsInstance(result['messages'][0], AIMessage)
            self.assertEqual(result['messages'][0].content, "✅ Appointment booked.")
            mock_insert.assert_called_once()

    def test_conditional_edge_stop(self):
        agent = CalendarAgent()
        state = {"messages": [AIMessage(content="STOP")] }
        self.assertEqual(agent.conditional_edge(state), END)
