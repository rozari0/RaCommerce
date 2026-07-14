from django.db import models
from django.utils.text import slugify
from django_lifecycle import BEFORE_CREATE, LifecycleModelMixin, hook

from .services import get_all_descendants


class Category(LifecycleModelMixin, models.Model):
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
        db_table = "categories"

    def related_products(self):
        category_ids = [self.id] + get_all_descendants(self.id)

        return Product.objects.filter(
            category_id__in=category_ids,
            status=Product.STATUS_CHOICES.ACTIVE,
            stock__gt=0,
        )

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @hook(BEFORE_CREATE)
    def update_slug(self):
        if self.name:
            self.slug = slugify(self.name)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        db_table = "products"

    def related_products(self):
        if self.category:
            return self.category.related_products().exclude(id=self.id)
        return Product.objects.none()

    class STATUS_CHOICES(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CHOICES.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
