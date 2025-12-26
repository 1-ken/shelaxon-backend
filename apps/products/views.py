from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Product, Category
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    CategorySerializer,
    ProductImageSerializer,
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Return root categories (no parent) with their subcategories nested
        # Or return all categories if 'all' query param is provided
        show_all = self.request.query_params.get('all')
        if show_all and show_all.lower() == 'true':
            return Category.objects.filter(is_active=True)
        # By default, return only root categories (parent=None)
        return Category.objects.filter(is_active=True, parent__isnull=True)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['unit_price', 'created_at', 'name']


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class WholesalerProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(wholesaler=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer


class WholesalerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(wholesaler=self.request.user)


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(id=product_id, wholesaler=request.user)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or you do not have permission'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
