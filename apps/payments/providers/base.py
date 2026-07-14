from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from django.http import HttpRequest

from apps.orders.models import Order
from apps.payments.models import Payment


@dataclass
class CheckoutData:
    redirect_url: str
    payment_id: int
    provider_session_id: str


@dataclass
class PaymentResult:
    success: bool
    transaction_id: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookResult:
    provider_name: str
    provider_session_id: str
    event: str


class PaymentProvider(ABC):
    @abstractmethod
    def create_checkout(self, order: Order, request: HttpRequest) -> CheckoutData: ...

    @abstractmethod
    def verify_payment(self, payment: Payment) -> PaymentResult: ...

    @abstractmethod
    def handle_webhook(self, request: HttpRequest) -> WebhookResult: ...
