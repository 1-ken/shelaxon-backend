"""
Product Serializers
"""

from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data


class ProductImageSerializer(serializers. ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers. CharField(source='category.name', read_only=True)
    wholesaler_name = serializers.CharField(source='wholesaler.business_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'wholesaler', 'wholesaler_name', 'category', 'category_name',
            'name', 'slug', 'description', 'sku', 'unit_price', 'bulk_price',
            'bulk_quantity', 'unit_of_measure', 'minimum_order_quantity',
            'stock_quantity', 'stock_status', 'is_active', 'is_featured',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['wholesaler', 'stock_status']


class ProductCreateSerializer(serializers. ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'description', 'sku', 'unit_price',
            'bulk_price', 'bulk_quantity', 'unit_of_measure',
            'minimum_order_quantity', 'stock_quantity', 'low_stock_threshold'
        ]

    def create(self, validated_data):
        validated_data['wholesaler'] = self.context['request']. user
        return super().create(validated_data)