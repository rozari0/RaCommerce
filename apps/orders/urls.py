from django.urls import path

from .views import CartItemDetailView, OrderItemView, UsersOrdersView

urlpatterns = [
    path("orders/", UsersOrdersView.as_view(), name="order-list"),
    path("orders/cart/", OrderItemView.as_view(), name="order-item-create"),
    path("orders/cart/<int:pk>/", CartItemDetailView.as_view(), name="cart-item-detail"),
]
