from django.db.models.fields import related
from rest_framework import serializers

from .models import Category, Product


class CategoryParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    parent = CategoryParentSerializer(read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent",
        queryset=Category.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent", "parent_id")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Product
        fields = "__all__"


class ProductSerializerSingle(ProductSerializer):
    related_products = serializers.SerializerMethodField()

    def get_related_products(self, obj):
        related_products = obj.related_products()
        return ProductSerializer(related_products, many=True).data

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sku",
            "description",
            "price",
            "stock",
            "status",
            "category",
            "related_products",
        )
