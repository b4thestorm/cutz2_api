# Stripe Integration

This feature implements a payment wall for platform access, specifically requiring payment to use the Barber Agent.

## Configuration

The following environment variables must be set in your `.env` file:

- `STRIPE_SECRET_KEY`: Your Stripe secret key.
- `STRIPE_PRICE_ID`: The ID of the product/price you are selling.
- `STRIPE_WEBHOOK_SECRET`: The secret for the Stripe webhook (used to verify events).
- `STRIPE_SUCCESS_URL`: The URL where users are redirected after a successful payment.
- `STRIPE_CANCEL_URL`: The URL where users are redirected if they cancel the payment.

## Flow

1. **Checkout Session**:
   - Endpoint: `/integrations/stripe_checkout/`
   - Action: An authenticated user requests a checkout session. The server creates a Stripe Session and returns a URL to the hosted checkout page.

2. **Webhook Handling**:
   - Endpoint: `/integrations/stripe_webhook/`
   - Action: Stripe sends a `checkout.session.completed` event. The server verifies the signature and updates the user's `is_platform_paid` status to `True` and stores the `stripe_customer_id`.

3. **Access Control**:
   - The `barber_agent` view in `cuts/chat/views.py` checks if the user has `is_platform_paid=True`.
   - If not paid, it returns a `402 Payment Required` response.

## Testing the Integration

- To manually mark a user as paid for testing purposes:
  `python manage.py shell`
  `from adminprofile.models import CustomUser; CustomUser.objects.filter(username='youruser').update(is_platform_paid=True)`
