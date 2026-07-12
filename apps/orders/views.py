from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError

from apps.orders.filters import OrderFilter
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import CartItemUpdateSerializer, OrderItemInputSerializer, OrderItemSerializer, OrderSerializer


class UsersOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema_view(
    post=extend_schema(
        request=OrderItemInputSerializer,
        responses={
            201: OrderItemSerializer,
            400: OpenApiResponse(description="Insufficient stock or invalid product/quantity"),
        }
    )
)
class OrderItemView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemInputSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        if quantity > product.stock:
            raise ValidationError(
                f"Insufficient stock. Available: {product.stock}, requested: {quantity}"
            )

        order, _ = Order.objects.get_or_create(
            user=self.request.user,
            status=Order.STATUS_CHOICES.PENDING,
        )

        item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            new_qty = item.quantity + quantity
            if new_qty > product.stock:
                raise ValidationError(
                    f"Insufficient stock. Available: {product.stock}, "
                    f"already in cart: {item.quantity}"
                )
            item.quantity = new_qty
            item.save()


@extend_schema_view(
    patch=extend_schema(
        request=CartItemUpdateSerializer,
        responses={
            200: OrderItemSerializer,
            400: OpenApiResponse(description="Insufficient stock or quantity=0 deletes item"),
        }
    ),
    delete=extend_schema(
        responses={204: None}
    )
)
class CartItemDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return CartItemUpdateSerializer
        return OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(
            order__user=self.request.user,
            order__status=Order.STATUS_CHOICES.PENDING,
        )

    def perform_update(self, serializer):
        quantity = serializer.validated_data["quantity"]
        item = serializer.instance

        if quantity == 0:
            return item.delete()

        if quantity > item.product.stock:
            raise ValidationError(
                f"Insufficient stock. Available: {item.product.stock}, requested: {quantity}"
            )

        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
