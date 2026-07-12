from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination

from apps.common.permissions import ReadOnlyOrStaff

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductListView(ListCreateAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrStaff]

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.STATUS_CHOICES.ACTIVE,
        )


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrStaff]

    def get_queryset(self):
        return Product.objects.all()


class CategoryListView(ListCreateAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrStaff]

    def get_queryset(self):
        return Category.objects.all()


class CategoryRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrStaff]

    queryset = Category.objects.all()
