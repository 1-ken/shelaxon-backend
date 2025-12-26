"""
Custom filters for product filtering
"""

import django_filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """Custom filter for products with enhanced category filtering"""
    
    category = django_filters.NumberFilter(method='filter_by_category')
    min_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = ['category', 'wholesaler', 'stock_status', 'min_price', 'max_price']
    
    def filter_by_category(self, queryset, name, value):
        """
        Filter products by category ID.
        If the category is a parent, include all products in subcategories.
        """
        try:
            category = Category.objects.get(id=value)
            # Get all subcategory IDs (including nested)
            category_ids = self._get_category_and_children_ids(category)
            return queryset.filter(category_id__in=category_ids)
        except Category.DoesNotExist:
            return queryset.none()
    
    def _get_category_and_children_ids(self, category):
        """Recursively get category ID and all descendant IDs"""
        ids = [category.id]
        for child in category.subcategories.filter(is_active=True):
            ids.extend(self._get_category_and_children_ids(child))
        return ids
