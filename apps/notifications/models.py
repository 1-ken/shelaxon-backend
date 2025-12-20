from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notifications"""

    class NotificationType(models.TextChoices):
        ORDER_PLACED = 'order_placed', 'Order Placed'
        ORDER_CONFIRMED = 'order_confirmed', 'Order Confirmed'
        ORDER_SHIPPED = 'order_shipped', 'Order Shipped'
        ORDER_DELIVERED = 'order_delivered', 'Order Delivered'
        PAYMENT_RECEIVED = 'payment_received', 'Payment Received'
        PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
        STOCK_LOW = 'stock_low', 'Stock Low'
        GENERAL = 'general', 'General'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
