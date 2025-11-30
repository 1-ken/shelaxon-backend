from django.urls import path
from .views import (
    CategoryListView,
    ProductListView,
    ProductDetailView,
    WholesalerProductListView,
    WholesalerProductDetailView,
    ProductImageUploadView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # Public product browsing
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Wholesaler product management
    path('my-products/', WholesalerProductListView.as_view(), name='my-products'),
    path('my-products/<int:pk>/', WholesalerProductDetailView.as_view(), name='my-product-detail'),
    path('my-products/<int:product_id>/images/', ProductImageUploadView.as_view(), name='product-image-upload'),
]