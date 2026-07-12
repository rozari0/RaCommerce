from django.urls import path

from .views import UsersOrdersView

urlpatterns = [
    path("orders/", UsersOrdersView.as_view(), name="order-list"),
]
