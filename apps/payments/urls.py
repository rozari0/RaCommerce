from django.urls import path

from .views import (
    CheckoutView,
    PaymentStatusView,
    bkash_callback_view,
    stripe_cancel_view,
    stripe_success_view,
    stripe_webhook_view,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/checkout/",
        CheckoutView.as_view(),
        name="checkout",
    ),
    path(
        "payments/<int:pk>/status/",
        PaymentStatusView.as_view(),
        name="payment-status",
    ),
    path(
        "payments/stripe/webhook/",
        stripe_webhook_view,
        name="stripe-webhook",
    ),
    path(
        "payments/stripe/success/",
        stripe_success_view,
        name="stripe-success",
    ),
    path(
        "payments/stripe/cancel/",
        stripe_cancel_view,
        name="stripe-cancel",
    ),
    path(
        "payments/bkash/callback/",
        bkash_callback_view,
        name="bkash-callback",
    ),
]
