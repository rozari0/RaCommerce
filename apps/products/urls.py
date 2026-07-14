from django.urls import path

from .views import (
    CategoryListView,
    CategoryProductsListView,
    CategoryRelatedProductsListView,
    CategoryRUDView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product"),
    path("category/", CategoryListView.as_view(), name="category-list"),
    path("category/<int:pk>/", CategoryRUDView.as_view(), name="category"),
    path(
        "category/<str:slug>/products/",
        CategoryProductsListView.as_view(),
        name="category-products",
    ),
    path(
        "category/<str:slug>/related-products/",
        CategoryRelatedProductsListView.as_view(),
        name="category-related-products",
    ),
]
