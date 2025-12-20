from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'wholesaler', 'category', 'unit_price', 'stock_quantity', 'stock_status']
    list_filter = ['category', 'stock_status', 'is_featured']
    search_fields = ['name', 'sku']


admin.site.register(ProductImage)
