from rest_framework.generics import ListAPIView
from .models import Product
from .serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination


class ProductListView(ListAPIView):
    pagination_class = PageNumberPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(
            status=Product.STATUS_CHOICES.ACTIVE,
        )
