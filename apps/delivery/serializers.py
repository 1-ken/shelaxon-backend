"""
Delivery Serializers
"""

from rest_framework import serializers
from .models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'order_number', 'driver_name', 'driver_phone',
            'vehicle_number', 'status', 'estimated_delivery_time',
            'actual_delivery_time', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
