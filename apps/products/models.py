"""
Product models for the marketplace
"""

from django.db import models
from django.conf import settings


class Category(models.Model):
    """Product categories"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcategories'
    )
    is_active = models. BooleanField(default=True)
    created_at = models. DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Products listed by wholesalers"""
    
    class StockStatus(models. TextChoices):
        IN_STOCK = 'in_stock', 'In Stock'
        LOW_STOCK = 'low_stock', 'Low Stock'
        OUT_OF_STOCK = 'out_of_stock', 'Out of Stock'
    
    wholesaler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models. CASCADE,
        related_name='products',
        limit_choices_to={'user_type': 'wholesaler'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    sku = models.CharField(max_length=100, unique=True)
    unit_price = models. DecimalField(max_digits=10, decimal_places=2)
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bulk_quantity = models. PositiveIntegerField(default=10, help_text="Minimum quantity for bulk price")
    unit_of_measure = models. CharField(max_length=50, default='piece')  # piece, kg, carton, etc. 
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    stock_quantity = models.PositiveIntegerField(default=0)
    stock_status = models. CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK
    )
    low_stock_threshold = models.PositiveIntegerField(default=10)
    is_active = models. BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models. DateTimeField(auto_now_add=True)
    updated_at = models. DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        unique_together = ['wholesaler', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-update stock status
        if self.stock_quantity == 0:
            self.stock_status = self. StockStatus.OUT_OF_STOCK
        elif self.stock_quantity <= self.low_stock_threshold:
            self.stock_status = self.StockStatus.LOW_STOCK
        else:
            self.stock_status = self. StockStatus.IN_STOCK
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Multiple images per product"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    is_primary = models. BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'

    def __str__(self):
        return f"Image for {self.product.name}"