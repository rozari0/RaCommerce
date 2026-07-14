from django.http import HttpRequest

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.providers.base import (
    CheckoutData,
    PaymentProvider,
    PaymentResult,
    WebhookResult,
)


class PaymentProcessor:
    _providers: dict[str, type[PaymentProvider]] = {}

    def __init__(self, provider_name: str):
        provider_cls = self._providers.get(provider_name)
        if provider_cls is None:
            msg = f"Unknown payment provider: {provider_name}"
            raise ValueError(msg)
        self._provider = provider_cls()

    @classmethod
    def register(cls, name: str):
        def wrapper(provider_cls: type[PaymentProvider]) -> type[PaymentProvider]:
            cls._providers[name] = provider_cls
            return provider_cls

        return wrapper

    @classmethod
    def get_choices(cls) -> list[tuple[str, str]]:
        return [(name, name.title()) for name in cls._providers]

    def create_checkout(self, order: Order, request: HttpRequest) -> CheckoutData:
        return self._provider.create_checkout(order, request)

    def verify_payment(self, payment: Payment) -> PaymentResult:
        return self._provider.verify_payment(payment)

    def handle_webhook(self, request: HttpRequest) -> WebhookResult:
        return self._provider.handle_webhook(request)
