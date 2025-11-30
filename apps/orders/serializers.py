"""
Order Serializers
"""

from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem
from apps.products.serializers import ProductSerializer


class OrderItemSerializer(serializers. ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['product_name', 'unit_price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    retailer_name = serializers. CharField(source='retailer.business_name', read_only=True)
    wholesaler_name = serializers.CharField(source='wholesaler.business_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'retailer', 'retailer_name', 'wholesaler',
            'wholesaler_name', 'status', 'subtotal', 'delivery_fee', 'total_amount',
            'delivery_address', 'delivery_city', 'delivery_notes',
            'expected_delivery_date', 'is_paid', 'paid_at', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'order_number', 'retailer', 'subtotal', 'total_amount',
            'is_paid', 'paid_at'
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']


class CartSerializer(serializers. ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'updated_at']


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout process"""
    delivery_address = serializers.CharField()
    delivery_city = serializers.CharField()
    delivery_notes = serializers. CharField(required=False, allow_blank=True)