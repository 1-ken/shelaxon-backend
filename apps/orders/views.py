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


class CartItemView(APIView):
    """Add item to cart"""
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def post(self, request):
        from apps.products.models import Product
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        # Validate product exists and is active
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or is not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock availability
        if product.stock_quantity < quantity:
            return Response(
                {
                    'error': f'Insufficient stock. Only {product.stock_quantity} available.',
                    'available_stock': product.stock_quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check minimum order quantity
        if quantity < product.minimum_order_quantity:
            return Response(
                {
                    'error': f'Minimum order quantity is {product.minimum_order_quantity}',
                    'minimum_order_quantity': product.minimum_order_quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart, _ = Cart.objects.get_or_create(retailer=request.user)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            # Check if updated quantity exceeds stock
            if new_quantity > product.stock_quantity:
                return Response(
                    {
                        'error': f'Cannot add {quantity} more. Total would exceed available stock ({product.stock_quantity}).',
                        'current_quantity_in_cart': cart_item.quantity,
                        'available_stock': product.stock_quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
            message = f'Updated quantity of "{product.name}" to {cart_item.quantity}'
        else:
            message = f'Added "{product.name}" to cart'
        
        return Response(
            {
                'status': 'success',
                'message': message,
                'cart_item': {
                    'id': cart_item.id,
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': cart_item.quantity,
                    'unit_price': str(product.unit_price),
                    'total_price': str(cart_item.total_price)
                }
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class CartItemUpdateView(APIView):
    """Update or remove cart item"""
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_cart_item(self, pk, user):
        try:
            return CartItem.objects.get(pk=pk, cart__retailer=user)
        except CartItem.DoesNotExist:
            return None

    def put(self, request, pk):
        """Update cart item quantity"""
        from apps.products.models import Product
        
        cart_item = self.get_cart_item(pk, request.user)
        if not cart_item:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': 'Quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quantity = int(quantity)
        product = cart_item.product
        
        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than 0. Use DELETE to remove item.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check stock availability
        if quantity > product.stock_quantity:
            return Response(
                {
                    'error': f'Insufficient stock. Only {product.stock_quantity} available.',
                    'available_stock': product.stock_quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check minimum order quantity
        if quantity < product.minimum_order_quantity:
            return Response(
                {
                    'error': f'Minimum order quantity is {product.minimum_order_quantity}',
                    'minimum_order_quantity': product.minimum_order_quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'status': 'success',
            'message': f'Updated quantity of "{product.name}" to {quantity}',
            'cart_item': {
                'id': cart_item.id,
                'product_id': product.id,
                'product_name': product.name,
                'quantity': cart_item.quantity,
                'unit_price': str(product.unit_price),
                'total_price': str(cart_item.total_price)
            }
        })

    def patch(self, request, pk):
        """Partial update - same as PUT for quantity updates"""
        return self.put(request, pk)

    def delete(self, request, pk):
        """Remove item from cart"""
        cart_item = self.get_cart_item(pk, request.user)
        if not cart_item:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        return Response({
            'status': 'success',
            'message': f'Removed "{product_name}" from cart'
        })


class ClearCartView(APIView):
    """Clear all items from cart"""
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def delete(self, request):
        cart = Cart.objects.filter(retailer=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {'message': 'Cart is already empty'},
                status=status.HTTP_200_OK
            )
        
        items_count = cart.items.count()
        cart.items.all().delete()
        
        return Response({
            'status': 'success',
            'message': f'Cleared {items_count} item(s) from cart'
        })


# Order Views
class CheckoutView(APIView):
    """Convert cart to order(s)"""
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Optimized query with prefetch
        cart = Cart.objects.prefetch_related(
            'items__product__wholesaler'
        ).filter(retailer=request.user).first()
        
        if not cart or not cart.items.exists():
            return Response(
                {"error": "Cart is empty. Please add items before checkout."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate stock availability for all items before processing
        stock_errors = []
        for cart_item in cart.items.all():
            product = cart_item.product
            if not product.is_active:
                stock_errors.append(f'"{product.name}" is no longer available')
            elif cart_item.quantity > product.stock_quantity:
                stock_errors.append(
                    f'"{product.name}" has only {product.stock_quantity} in stock (you have {cart_item.quantity} in cart)'
                )
        
        if stock_errors:
            return Response(
                {
                    "error": "Some items in your cart have stock issues",
                    "stock_errors": stock_errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Group cart items by wholesaler
        items_by_wholesaler = {}
        for cart_item in cart.items.all():
            wholesaler = cart_item.product.wholesaler
            if wholesaler.id not in items_by_wholesaler:
                items_by_wholesaler[wholesaler.id] = {
                    'wholesaler': wholesaler,
                    'items': []
                }
            items_by_wholesaler[wholesaler.id]['items'].append(cart_item)
        
        orders = []
        order_items_to_create = []
        products_to_update = []
        
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
            
            # Prepare order items for bulk create
            for cart_item in data['items']:
                product = cart_item.product
                unit_price = (
                    product.bulk_price
                    if cart_item.quantity >= product.bulk_quantity and product.bulk_price
                    else product.unit_price
                )
                
                order_items_to_create.append(OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    total_price=cart_item.quantity * unit_price
                ))
                
                # Update stock
                product.stock_quantity -= cart_item.quantity
                products_to_update.append(product)
            
            orders.append(order)
        
        # Bulk create order items (single query instead of multiple)
        OrderItem.objects.bulk_create(order_items_to_create)
        
        # Bulk update product stock (optimized)
        from apps.products.models import Product
        for product in products_to_update:
            product.save()  # Triggers stock_status update in model
        
        # Clear cart
        cart.delete()
        
        # Prefetch items for response
        order_ids = [o.id for o in orders]
        orders_with_items = Order.objects.prefetch_related('items').filter(id__in=order_ids)
        
        return Response(
            {
                'status': 'success',
                'message': f'Successfully created {len(orders)} order(s)',
                'orders': OrderSerializer(orders_with_items, many=True).data
            },
            status=status.HTTP_201_CREATED
        )


class RetailerOrderListView(generics.ListAPIView):
    """List retailer's orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsRetailer]

    def get_queryset(self):
        return Order.objects.filter(
            retailer=self.request.user
        ).select_related(
            'wholesaler'
        ).prefetch_related(
            'items__product'
        ).order_by('-created_at')


class WholesalerOrderListView(generics.ListAPIView):
    """List wholesaler's received orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsWholesaler]

    def get_queryset(self):
        return Order.objects.filter(
            wholesaler=self.request.user
        ).select_related(
            'retailer'
        ).prefetch_related(
            'items__product'
        ).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(retailer=user) | Q(wholesaler=user)
        ).select_related(
            'retailer', 'wholesaler'
        ).prefetch_related(
            'items__product'
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Update order status (wholesaler only)"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsWholesaler]

    # Valid status transitions
    VALID_TRANSITIONS = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['processing', 'cancelled'],
        'processing': ['out_for_delivery', 'cancelled'],
        'out_for_delivery': ['delivered'],
        'delivered': [],  # Final state
        'cancelled': [],  # Final state
        'refunded': [],   # Final state
    }

    def get_queryset(self):
        return Order.objects.filter(
            wholesaler=self.request.user
        ).select_related('retailer', 'wholesaler').prefetch_related('items')

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {
                    "error": "Status is required",
                    "valid_statuses": list(dict(Order.OrderStatus.choices).keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Order.OrderStatus.choices):
            return Response(
                {
                    "error": f"Invalid status '{new_status}'",
                    "valid_statuses": list(dict(Order.OrderStatus.choices).keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check valid transition
        current_status = order.status
        valid_next = self.VALID_TRANSITIONS.get(current_status, [])
        
        if new_status not in valid_next:
            return Response(
                {
                    "error": f"Cannot change status from '{current_status}' to '{new_status}'",
                    "current_status": current_status,
                    "valid_transitions": valid_next
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # TODO: Trigger notification to retailer
        
        return Response({
            'status': 'success',
            'message': f'Order {order.order_number} status updated from "{old_status}" to "{new_status}"',
            'order': OrderSerializer(order).data
        })