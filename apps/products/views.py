from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination

from apps.common.permissions import ReadOnlyOrStaff

from .models import Product
from .serializers import ProductSerializer


class ProductListView(ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.STATUS_CHOICES.ACTIVE,
        )


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrStaff]

    def get_queryset(self):
        return Product.objects.all()
