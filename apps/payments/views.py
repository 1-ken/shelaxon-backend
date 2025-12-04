"""
Payment Views
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from . models import Payment
from .serializers import PaymentSerializer, MpesaPaymentSerializer
from apps.orders.models import Order
from utils.mpesa import MpesaClient


class InitiateMpesaPaymentView(APIView):
    """Initiate M-Pesa STK Push payment"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MpesaPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        phone_number = serializer.validated_data['phone_number']
        
        try:
            order = Order.objects.get(
                id=order_id,
                retailer=request.user,
                is_paid=False
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found or already paid"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method=Payment.PaymentMethod.MPESA,
            phone_number=phone_number
        )
        
        # Initiate STK Push
        mpesa = MpesaClient()
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=order.total_amount,
            account_reference=order.order_number,
            transaction_desc=f"Payment for order {order.order_number}"
        )
        
        if response.get('ResponseCode') == '0':
            payment.mpesa_checkout_request_id = response.get('CheckoutRequestID')
            payment.status = Payment.PaymentStatus.PROCESSING
            payment.save()
            
            return Response({
                "message": "Payment initiated.  Check your phone for M-Pesa prompt.",
                "checkout_request_id": response.get('CheckoutRequestID'),
                "payment_id": payment.id
            })
        else:
            payment.status = Payment.PaymentStatus.FAILED
            payment.failure_reason = response.get('errorMessage', 'Unknown error')
            payment.save()
            
            return Response(
                {"error": "Failed to initiate payment", "details": response},
                status=status.HTTP_400_BAD_REQUEST
            )


class MpesaCallbackView(APIView):
    """Handle M-Pesa callback"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        
        # Extract callback data
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        
        try:
            payment = Payment.objects.get(
                mpesa_checkout_request_id=checkout_request_id
            )
        except Payment.DoesNotExist:
            return Response({"ResultCode": 1, "ResultDesc": "Payment not found"})
        
        if result_code == 0:
            # Payment successful
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.mpesa_receipt_number = item.get('Value')
            
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update order
            order = payment.order
            order.is_paid = True
            order.paid_at = timezone.now()
            order.status = Order.OrderStatus.CONFIRMED
            order.save()
            
            # TODO: Send notification to retailer and wholesaler
            
        else:
            payment.status = Payment.PaymentStatus.FAILED
            payment.failure_reason = stk_callback.get('ResultDesc', 'Payment failed')
            payment.save()
        
        return Response({"ResultCode": 0, "ResultDesc": "Callback received"})


class PaymentListView(generics.ListAPIView):
    """List user's payments"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'retailer':
            return Payment.objects.filter(order__retailer=user)
        return Payment.objects.filter(order__wholesaler=user)


class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment details"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'retailer':
            return Payment.objects.filter(order__retailer=user)
        return Payment.objects.filter(order__wholesaler=user)
