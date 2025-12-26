"""
User Views
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    WholesalerProfileSerializer,
    ProfileUpdateSerializer,
    CustomTokenObtainPairSerializer,
    AdminPasswordResetSerializer,
    ChangePasswordSerializer,
)
from .models import WholesalerProfile, RetailerProfile

User = get_user_model()

# Default password for admin reset
DEFAULT_RESET_PASSWORD = getattr(settings, 'DEFAULT_RESET_PASSWORD', 'Reset@123')


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login view that returns clearer auth errors."""

    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Register a new user (retailer or wholesaler). Returns user data and JWT tokens.',
    request=UserRegistrationSerializer,
    examples=[
        OpenApiExample(
            'Registration Example',
            value={
                'username': 'retailconnect_ke001',
                'phone_number': '+254712345678',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
                'user_type': 'retailer',
                'business_name': 'My Shop',
                'city': 'Nairobi'
            },
            request_only=True
        )
    ]
)
class UserRegistrationView(generics.CreateAPIView):
    """Register a new user (retailer or wholesaler)"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Profile'],
    summary='Get current user profile',
    description='Retrieve the authenticated user\'s profile information.'
)
class UserProfileView(generics.RetrieveAPIView):
    """Get current user profile (read-only)"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Wholesalers'])
class WholesalerListView(generics.ListAPIView):
    """List all wholesalers"""
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = WholesalerProfile.objects.select_related('user').all()
        city = self.request.query_params.get('city')
        verified = self.request.query_params.get('verified')
        if city:
            queryset = queryset.filter(user__city__icontains=city)
        if verified and verified.lower() == 'true':
            queryset = queryset.filter(user__is_verified=True)
        return queryset


@extend_schema(tags=['Wholesalers'])
class WholesalerDetailView(generics.RetrieveAPIView):
    """Get wholesaler details"""
    queryset = WholesalerProfile.objects.all()
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    tags=['Profile'],
    summary='Update user profile',
    description='Update user profile details. All fields are optional - you can update a single field or multiple fields at once. Uses PATCH for partial updates.',
    request=ProfileUpdateSerializer,
    examples=[
        OpenApiExample(
            'Update single field',
            value={
                'username': 'new_username'
            },
            request_only=True,
            description='Update only the username'
        ),
        OpenApiExample(
            'Update multiple fields',
            value={
                'email': 'newemail@example.com',
                'phone_number': '+254712345678',
                'business_name': 'My New Shop',
                'location': 'Westlands, Nairobi',
                'city': 'Nairobi',
                'profile_image': 'https://example.com/images/profile.jpg'
            },
            request_only=True,
            description='Update multiple profile fields'
        )
    ]
)
class ProfileUpdateView(generics.GenericAPIView):
    """Update user profile details (username, email, phone_number, business_name, location, city, profile_image)"""
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']  # Only allow PATCH method

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        """Partial update - only update fields that are provided"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(instance).data
        })


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


@extend_schema(
    tags=['Admin - Password Management'],
    summary='Reset user password (Admin only)',
    description='Allows admin/superuser to reset any user\'s password. If no new_password is provided, the default password "Reset@123" will be used.',
    request=AdminPasswordResetSerializer,
    examples=[
        OpenApiExample(
            'Reset with default password',
            value={'user_id': 1},
            request_only=True,
            description='Reset to default password (Reset@123)'
        ),
        OpenApiExample(
            'Reset with custom password',
            value={'user_id': 1, 'new_password': 'NewSecurePass123!'},
            request_only=True,
            description='Reset to a custom password'
        )
    ]
)
class AdminPasswordResetView(APIView):
    """Admin endpoint to reset user passwords"""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = AdminPasswordResetSerializer

    def post(self, request):
        serializer = AdminPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        new_password = serializer.validated_data.get('new_password') or DEFAULT_RESET_PASSWORD
        
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': f'Password for user "{user.username}" has been reset successfully.',
            'user_id': user.id,
            'username': user.username,
            'default_password_used': not serializer.validated_data.get('new_password')
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Profile'],
    summary='Change own password',
    description='Allows authenticated users to change their own password.',
    request=ChangePasswordSerializer,
    examples=[
        OpenApiExample(
            'Change password',
            value={
                'old_password': 'CurrentPass123!',
                'new_password': 'NewSecurePass456!',
                'confirm_password': 'NewSecurePass456!'
            },
            request_only=True
        )
    ]
)
class ChangePasswordView(APIView):
    """Endpoint for users to change their own password"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully. Please login with your new password.'
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Admin - User Management'],
    summary='List all users (Admin only)',
    description='Allows admin/superuser to view all users in the system.'
)
class AdminUserListView(generics.ListAPIView):
    """Admin endpoint to list all users"""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


@extend_schema(
    tags=['Admin - User Management'],
    summary='Get user details (Admin only)',
    description='Allows admin/superuser to view any user\'s details.'
)
class AdminUserDetailView(generics.RetrieveAPIView):
    """Admin endpoint to get user details"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
