from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderItemInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "quantity")


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("quantity",)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        # fields = "__all__"
        exclude = ("user",)
