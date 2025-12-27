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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {
                'status': 'success',
                'message': f'Product "{product_name}" has been deleted successfully.'
            },
            status=status.HTTP_200_OK
        )


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        from .models import ProductImage
        
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
        
        # Handle primary image - only one primary image per product
        is_primary = serializer.validated_data.get('is_primary', False)
        if is_primary:
            # Remove primary status from all other images of this product
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
        
        # If this is the first image, make it primary automatically
        if not product.images.exists():
            serializer.validated_data['is_primary'] = True
        
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductImageDeleteView(generics.DestroyAPIView):
    """Delete a product image"""
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .models import ProductImage
        # Only allow deleting images from products owned by the user
        return ProductImage.objects.filter(product__wholesaler=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product = instance.product
        was_primary = instance.is_primary
        
        self.perform_destroy(instance)
        
        # If deleted image was primary, set another image as primary
        if was_primary:
            remaining_image = product.images.first()
            if remaining_image:
                remaining_image.is_primary = True
                remaining_image.save()
        
        return Response(
            {
                'status': 'success',
                'message': 'Image deleted successfully.'
            },
            status=status.HTTP_200_OK
        )


class ProductImageSetPrimaryView(generics.UpdateAPIView):
    """Set an image as the primary image for a product"""
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .models import ProductImage
        return ProductImage.objects.filter(product__wholesaler=self.request.user)

    def update(self, request, *args, **kwargs):
        from .models import ProductImage
        
        instance = self.get_object()
        product = instance.product
        
        # Remove primary status from all other images
        ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
        
        # Set this image as primary
        instance.is_primary = True
        instance.save()
        
        return Response(
            {
                'status': 'success',
                'message': 'Image set as primary successfully.',
                'image': ProductImageSerializer(instance).data
            },
            status=status.HTTP_200_OK
        )
