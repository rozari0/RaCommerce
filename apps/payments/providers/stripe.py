from decimal import Decimal

import stripe
from django.conf import settings
from django.http import HttpRequest

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.processors import PaymentProcessor
from apps.payments.providers.base import (
    CheckoutData,
    PaymentProvider,
    PaymentResult,
    WebhookResult,
)


@PaymentProcessor.register("stripe")
class StripeProvider(PaymentProvider):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout(self, order: Order, request: HttpRequest) -> CheckoutData:
        line_items = []
        for item in order.items.all():
            line_items.append(
                {
                    "price_data": {
                        "currency": "bdt",
                        "product_data": {"name": item.product.name},
                        "unit_amount": int(item.price * Decimal("100")),
                    },
                    "quantity": item.quantity,
                }
            )

        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri("/api/payments/stripe/success/")
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/api/payments/stripe/cancel/"),
            metadata={"order_id": str(order.id)},
        )

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            provider=Payment.Provider.STRIPE,
            transaction_id=session.id,
            status=Payment.Status.PENDING,
            raw_response={"stripe_session_id": session.id},
        )

        return CheckoutData(
            redirect_url=session.url,
            payment_id=payment.id,
            provider_session_id=session.id,
        )

    def verify_payment(self, payment: Payment) -> PaymentResult:
        session = stripe.checkout.Session.retrieve(payment.transaction_id)
        success = session.payment_status == "paid"
        return PaymentResult(
            success=success,
            transaction_id=getattr(session, "payment_intent", None)
            if success
            else None,
            raw_response={"payment_status": session.payment_status},
        )

    def handle_webhook(self, request: HttpRequest) -> WebhookResult:
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        session = event.data.object
        return WebhookResult(
            provider_name="stripe",
            provider_session_id=session.id,
            event=event.type,
        )
