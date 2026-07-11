from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from apps.products.models import Product
from django_lifecycle import LifecycleModelMixin, hook, BEFORE_SAVE, AFTER_SAVE

User = get_user_model()


class Order(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.0")
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CHOICES.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - User {self.user.id} - Status {self.status}"

    def calculate_total_amount(self):
        total = self.items.aggregate(total=models.Sum("subtotal"))["total"] or Decimal(
            "0.0"
        )
        self.total_amount = total
        self.save(update_fields=["total_amount"])
        return total

    def can_checkout(self):
        return self.status == self.STATUS_CHOICES.PENDING


class OrderItem(LifecycleModelMixin, models.Model):
    class Meta:
        db_table = "order_items"
        unique_together = ("order", "product")

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    @hook(BEFORE_SAVE)
    def update_subtotal(self):
        self.subtotal = self.price * self.quantity

    @hook(AFTER_SAVE)
    def update_order_total(self):
        self.order.calculate_total_amount()

    def __str__(self):
        return (
            f"OrderItem {self.id} - Order {self.order.id} - Product {self.product.id}"
        )
