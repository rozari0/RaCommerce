from django.conf import settings
from django.http import HttpRequest
from pybkash import Client, Token

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.processors import PaymentProcessor
from apps.payments.providers.base import (
    CheckoutData,
    PaymentProvider,
    PaymentResult,
    WebhookResult,
)


@PaymentProcessor.register("bkash")
class BkashProvider(PaymentProvider):
    def _get_client(self) -> Client:
        token = Token(
            username=settings.BKASH_USERNAME,
            password=settings.BKASH_PASSWORD,
            app_key=settings.BKASH_APP_KEY,
            app_secret=settings.BKASH_APP_SECRET,
            sandbox=settings.BKASH_SANDBOX,
        )
        return Client(token)

    def create_checkout(self, order: Order, request: HttpRequest) -> CheckoutData:
        client = self._get_client()
        try:
            payment = client.create_payment(
                callback_url=request.build_absolute_uri(
                    "/api/payments/bkash/callback/"
                ),
                payer_reference=str(order.user.id),
                amount=int(order.total_amount),
                invoice_number=str(order.id),
            )

            payment_record = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                provider=Payment.Provider.BKASH,
                transaction_id=payment.payment_id,
                status=Payment.Status.PENDING,
                raw_response={
                    "bkash_payment_id": payment.payment_id,
                    "bkash_url": payment.bkash_url,
                },
            )

            return CheckoutData(
                redirect_url=payment.bkash_url,
                payment_id=payment_record.id,
                provider_session_id=payment.payment_id,
            )
        finally:
            client.close()

    def verify_payment(self, payment: Payment) -> PaymentResult:
        client = self._get_client()
        try:
            execution = client.execute_payment(payment.transaction_id)
            success = execution.is_complete()
            return PaymentResult(
                success=success,
                transaction_id=execution.trx_id if success else None,
                raw_response={
                    "status": execution.status,
                    "trx_id": execution.trx_id,
                    "amount": execution.amount,
                },
            )
        finally:
            client.close()

    def handle_webhook(self, request: HttpRequest) -> WebhookResult:
        msg = "bKash uses callback redirect, not webhooks"
        raise NotImplementedError(msg)
