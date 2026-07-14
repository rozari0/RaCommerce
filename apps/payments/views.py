from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.processors import PaymentProcessor
from apps.payments.serializers import (
    CheckoutInputSerializer,
    CheckoutResponseSerializer,
    PaymentStatusSerializer,
)


class CheckoutView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutInputSerializer

    @extend_schema(
        request=CheckoutInputSerializer,
        responses={
            201: CheckoutResponseSerializer,
            400: OpenApiResponse(description="Invalid provider or order"),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get("order_id")
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not order.can_checkout():
            return Response(
                {"detail": "Order is not available for checkout."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_name = serializer.validated_data["provider"]
        processor = PaymentProcessor(provider_name)
        checkout_data = processor.create_checkout(order, request)

        return Response(
            CheckoutResponseSerializer(checkout_data).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentStatusSerializer
    queryset = Payment.objects.all()

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


@require_GET
def stripe_success_view(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return HttpResponseRedirect(
            settings.FRONTEND_URL or "/"
        )

    try:
        payment = Payment.objects.get(
            transaction_id=session_id,
            provider=Payment.Provider.STRIPE,
        )
    except Payment.DoesNotExist:
        return HttpResponseRedirect(
            settings.FRONTEND_URL or "/"
        )

    processor = PaymentProcessor("stripe")
    result = processor.verify_payment(payment)

    if result.success:
        payment.status = Payment.Status.COMPLETED
        payment.transaction_id = result.transaction_id or payment.transaction_id
        payment.raw_response = result.raw_response
        payment.save()

        order = payment.order
        order.status = Order.STATUS_CHOICES.PAID
        order.save()

    redirect_url = (
        f"{settings.FRONTEND_URL}/orders/{payment.order.id}"
        if settings.FRONTEND_URL
        else "/"
    )
    params = urlencode({"payment_id": payment.id, "status": payment.status})
    return HttpResponseRedirect(f"{redirect_url}?{params}")


@require_GET
def stripe_cancel_view(request):
    redirect_url = settings.FRONTEND_URL or "/"
    return HttpResponseRedirect(redirect_url)


@require_GET
def bkash_callback_view(request):
    payment_id = request.GET.get("paymentID")
    bkash_status = request.GET.get("status")

    if not payment_id or bkash_status != "success":
        redirect_url = (
            f"{settings.FRONTEND_URL}/orders"
            if settings.FRONTEND_URL
            else "/"
        )
        return HttpResponseRedirect(
            f"{redirect_url}?payment_error=cancelled"
        )

    try:
        payment = Payment.objects.get(
            transaction_id=payment_id,
            provider=Payment.Provider.BKASH,
        )
    except Payment.DoesNotExist:
        return HttpResponseRedirect(
            f"{settings.FRONTEND_URL or '/'}?payment_error=not_found"
        )

    processor = PaymentProcessor("bkash")
    result = processor.verify_payment(payment)

    if result.success:
        payment.status = Payment.Status.COMPLETED
        payment.transaction_id = result.transaction_id or payment.transaction_id
        payment.raw_response = result.raw_response
        payment.save()

        order = payment.order
        order.status = Order.STATUS_CHOICES.PAID
        order.save()
    else:
        payment.status = Payment.Status.FAILED
        payment.raw_response = result.raw_response
        payment.save()

    redirect_url = (
        f"{settings.FRONTEND_URL}/orders/{payment.order.id}"
        if settings.FRONTEND_URL
        else "/"
    )
    params = urlencode({"payment_id": payment.id, "status": payment.status})
    return HttpResponseRedirect(f"{redirect_url}?{params}")


@api_view(["POST"])
def stripe_webhook_view(request):
    processor = PaymentProcessor("stripe")
    try:
        webhook_result = processor.handle_webhook(request)
    except ValueError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if webhook_result.event == "checkout.session.completed":
        try:
            payment = Payment.objects.get(
                transaction_id=webhook_result.provider_session_id,
                provider=Payment.Provider.STRIPE,
            )
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        result = processor.verify_payment(payment)
        if result.success:
            payment.status = Payment.Status.COMPLETED
            payment.transaction_id = (
                result.transaction_id or payment.transaction_id
            )
            payment.raw_response = result.raw_response
            payment.save()

            order = payment.order
            order.status = Order.STATUS_CHOICES.PAID
            order.save()

    return Response(status=status.HTTP_200_OK)
