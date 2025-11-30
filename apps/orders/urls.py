"""
Order URLs
"""

from django.urls import path
from .views import (
    CartView,
    CartItemView,
    CartItemUpdateView,
    ClearCartView,
    CheckoutView,
    RetailerOrderListView,
    WholesalerOrderListView,
    OrderDetailView,
    OrderStatusUpdateView
)

urlpatterns = [
    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/', CartItemView.as_view(), name='cart-add-item'),
    path('cart/items/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    path('cart/clear/', ClearCartView.as_view(), name='cart-clear'),
    
    # Checkout
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    
    # Orders
    path('my-orders/', RetailerOrderListView.as_view(), name='retailer-orders'),
    path('received-orders/', WholesalerOrderListView.as_view(), name='wholesaler-orders'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]