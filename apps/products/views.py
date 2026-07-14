from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import LimitOffsetPagination

from apps.common.permissions import ReadOnlyOrStaff

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductSerializerSingle


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

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductSerializerSingle
        return ProductSerializer

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


class CategoryProductsListView(ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return Product.objects.filter(
            category__slug=slug,
            status=Product.STATUS_CHOICES.ACTIVE,
        )


class CategoryRelatedProductsListView(ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        category = Category.objects.filter(slug=slug).first()
        if not category:
            return Product.objects.none()
        return category.related_products()
