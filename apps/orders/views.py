"""
Order Views
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django. db.models import Q
from . models import Order, OrderItem, Cart, CartItem
from .serializers import (
    OrderSerializer,
    CartSerializer,
    CartItemSerializer,
    CheckoutSerializer
)


class IsRetailer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'retailer'


class IsWholesaler(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'wholesaler'


# Cart Views
class CartView(generics.RetrieveAPIView):
    """Get current user's cart"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(retailer=self.request.user)
        return cart


class CartItemView(generics.CreateAPIView):
    """Add item to cart"""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(retailer=self.request.user)
        product_id = self.request.data.get('product_id')
        quantity = int(self.request.data.get('quantity', 1))
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()


class CartItemUpdateView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Update or remove cart item"""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_queryset(self):
        return CartItem.objects.filter(cart__retailer=self.request.user)


class ClearCartView(APIView):
    """Clear all items from cart"""
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def delete(self, request):
        Cart.objects.filter(retailer=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Order Views
class CheckoutView(APIView):
    """Convert cart to order(s)"""
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart = Cart.objects.filter(retailer=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Group cart items by wholesaler
        items_by_wholesaler = {}
        for cart_item in cart.items.select_related('product__wholesaler'):
            wholesaler = cart_item.product.wholesaler
            if wholesaler.id not in items_by_wholesaler:
                items_by_wholesaler[wholesaler.id] = {
                    'wholesaler': wholesaler,
                    'items': []
                }
            items_by_wholesaler[wholesaler.id]['items'].append(cart_item)
        
        orders = []
        
        # Create order for each wholesaler
        for wholesaler_id, data in items_by_wholesaler.items():
            subtotal = sum(item.total_price for item in data['items'])
            delivery_fee = 100  # Could be calculated based on location
            
            order = Order.objects.create(
                retailer=request.user,
                wholesaler=data['wholesaler'],
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total_amount=subtotal + delivery_fee,
                delivery_address=serializer.validated_data['delivery_address'],
                delivery_city=serializer.validated_data['delivery_city'],
                delivery_notes=serializer.validated_data.get('delivery_notes', '')
            )
            
            # Create order items
            for cart_item in data['items']:
                product = cart_item.product
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    unit_price=(
                        product.bulk_price
                        if cart_item.quantity >= product.bulk_quantity
                        and product.bulk_price
                        else product.unit_price
                    ),
                )
                
                # Update stock
                product.stock_quantity -= cart_item.quantity
                product.save()
            
            orders.append(order)
        
        # Clear cart
        cart.delete()
        
        return Response(
            OrderSerializer(orders, many=True).data,
            status=status.HTTP_201_CREATED
        )


class RetailerOrderListView(generics.ListAPIView):
    """List retailer's orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_queryset(self):
        return Order.objects.filter(retailer=self.request.user)


class WholesalerOrderListView(generics.ListAPIView):
    """List wholesaler's received orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsWholesaler]

    def get_queryset(self):
        return Order.objects.filter(wholesaler=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(retailer=user) | Q(wholesaler=user)
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Update order status (wholesaler only)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsWholesaler]

    def get_queryset(self):
        return Order.objects.filter(wholesaler=self.request.user)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.OrderStatus.choices):
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        # TODO: Trigger notification to retailer
        
        return Response(OrderSerializer(order).data)