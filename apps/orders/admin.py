from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'retailer', 'wholesaler', 'status', 'total_amount', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'created_at']
    inlines = [OrderItemInline]


admin.site.register(Cart)
admin.site.register(CartItem)