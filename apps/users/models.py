"""
User models for Retailers and Wholesalers
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    """Custom User model for RetailConnect Kenya"""
    
    class UserType(models.TextChoices):
        RETAILER = 'retailer', 'Retailer'
        WHOLESALER = 'wholesaler', 'Wholesaler'
        ADMIN = 'admin', 'Admin'
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.RETAILER
    )
    phone_number = PhoneNumberField(unique=True, region='KE')
    business_name = models.CharField(max_length=255)
    business_registration_number = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.business_name} ({self.user_type})"


class WholesalerProfile(models.Model):
    """Extended profile for wholesalers"""
    
    class SubscriptionPlan(models.TextChoices):
        FREE = 'free', 'Free'
        BASIC = 'basic', 'Basic'
        PREMIUM = 'premium', 'Premium'
        ENTERPRISE = 'enterprise', 'Enterprise'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wholesaler_profile'
    )
    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE
    )
    subscription_expiry = models.DateField(blank=True, null=True)
    categories = models.ManyToManyField('products.Category', blank=True)
    description = models.TextField(blank=True)
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    delivery_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'wholesaler_profiles'

    def __str__(self):
        return f"Wholesaler: {self.user.business_name}"


class RetailerProfile(models.Model):
    """Extended profile for retailers"""
    
    class BusinessType(models.TextChoices):
        SHOP = 'shop', 'Shop'
        KIOSK = 'kiosk', 'Kiosk'
        MINIMART = 'minimart', 'Minimart'
        SUPERMARKET = 'supermarket', 'Supermarket'
        OTHER = 'other', 'Other'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='retailer_profile'
    )
    business_type = models.CharField(
        max_length=20,
        choices=BusinessType.choices,
        default=BusinessType.SHOP
    )
    preferred_wholesalers = models.ManyToManyField(
        User,
        related_name='preferred_by_retailers',
        blank=True,
        limit_choices_to={'user_type': 'wholesaler'}
    )
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = 'retailer_profiles'

    def __str__(self):
        return f"Retailer: {self.user.business_name}"