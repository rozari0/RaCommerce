from django_filters import rest_framework as filters

from .models import Order


class OrderFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Order.STATUS_CHOICES.choices)
    min_total = filters.NumberFilter(field_name="total_amount", lookup_expr="gte")
    max_total = filters.NumberFilter(field_name="total_amount", lookup_expr="lte")
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Order
        fields = [
            "status",
            "user",
        ]
