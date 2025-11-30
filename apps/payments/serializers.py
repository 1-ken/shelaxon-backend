"""
Payment Serializers
"""

from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'order', 'amount', 'payment_method',
            'status', 'phone_number', 'mpesa_receipt_number', 'created_at',
            'completed_at'
        ]
        read_only_fields = [
            'transaction_id', 'status', 'mpesa_receipt_number',
            'created_at', 'completed_at'
        ]


class MpesaPaymentSerializer(serializers.Serializer):
    """Serializer for initiating M-Pesa payment"""
    order_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        # Format phone number to 254XXXXXXXXX
        phone = value.replace('+', '').replace(' ', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        if not phone.startswith('254') or len(phone) != 12:
            raise serializers.ValidationError("Invalid phone number format")
        return phone