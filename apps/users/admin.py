from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WholesalerProfile, RetailerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'business_name', 'user_type', 'city', 'is_verified']
    list_filter = ['user_type', 'is_verified', 'city']


admin.site.register(WholesalerProfile)
admin.site.register(RetailerProfile)
