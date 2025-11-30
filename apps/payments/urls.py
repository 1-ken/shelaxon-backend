from django.urls import path
from . views import InitiateMpesaPaymentView, MpesaCallbackView, PaymentListView, PaymentDetailView

urlpatterns = [
    path('mpesa/initiate/', InitiateMpesaPaymentView. as_view(), name='mpesa-initiate'),
    path('mpesa/callback/', MpesaCallbackView. as_view(), name='mpesa-callback'),
    path('', PaymentListView. as_view(), name='payment-list'),
    path('<int:pk>/', PaymentDetailView. as_view(), name='payment-detail'),
]
