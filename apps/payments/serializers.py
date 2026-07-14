from rest_framework import serializers

from apps.payments.models import Payment
from apps.payments.processors import PaymentProcessor


class CheckoutInputSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=PaymentProcessor.get_choices())


class CheckoutResponseSerializer(serializers.Serializer):
    redirect_url = serializers.URLField()
    payment_id = serializers.IntegerField()


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "amount",
            "status",
            "provider",
            "transaction_id",
            "created_at",
        ]


class StripeSuccessQuerySerializer(serializers.Serializer):
    session_id = serializers.CharField()


class BkashCallbackQuerySerializer(serializers.Serializer):
    paymentID = serializers.CharField()
    status = serializers.CharField()
