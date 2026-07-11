from django.db import models

from apps.orders.models import Order


class Payment(models.Model):
    class Meta:
        ordering = ["-created_at"]
        db_table = "payments"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        BKASH = "bkash", "Bkash"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status, default=Status.PENDING)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    transaction_id = models.CharField(max_length=255, unique=True, db_index=True)
    raw_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"
