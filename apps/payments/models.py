"""
Payment models
"""

from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    """Payment transactions"""
    
    class PaymentMethod(models.TextChoices):
        MPESA = 'mpesa', 'M-Pesa'
        CARD = 'card', 'Card Payment'
        BANK = 'bank', 'Bank Transfer'
    
    class PaymentStatus(models. TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    transaction_id = models. CharField(max_length=100, unique=True, editable=False)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models. DecimalField(max_digits=12, decimal_places=2)
    payment_method = models. CharField(
        max_length=20,
        choices=PaymentMethod. choices,
        default=PaymentMethod. MPESA
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus. choices,
        default=PaymentStatus. PENDING
    )
    phone_number = models.CharField(max_length=20, blank=True)
    mpesa_receipt_number = models. CharField(max_length=50, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True)
    failure_reason = models. TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models. DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

    def save(self, *args, **kwargs):
        if not self. transaction_id:
            self.transaction_id = f"PAY-{uuid. uuid4().hex[:12]. upper()}"
        super().save(*args, **kwargs)