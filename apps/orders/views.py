from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.orders.filters import OrderFilter
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


class UsersOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
