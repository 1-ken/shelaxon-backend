"""
User Views
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    WholesalerProfileSerializer,
    RetailerProfileUpdateSerializer,
    CustomTokenObtainPairSerializer,
)
from .models import WholesalerProfile, RetailerProfile

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login view that returns clearer auth errors."""

    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"


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


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class WholesalerListView(generics.ListAPIView):
    """List all wholesalers"""
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = WholesalerProfile.objects.filter(user__is_verified=True)
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(user__city__icontains=city)
        return queryset


class WholesalerDetailView(generics.RetrieveAPIView):
    """Get wholesaler details"""
    queryset = WholesalerProfile.objects.all()
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class RetailerProfileUpdateView(generics.UpdateAPIView):
    """Update retailer profile details (email, business_registration_number, location)"""
    serializer_class = RetailerProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Check if user is a retailer
        if self.request.user.user_type != 'retailer':
            return Response(
                {'error': 'Only retailers can update retailer profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'message': 'Retailer profile updated successfully',
            'user': UserSerializer(instance).data
        }, status=status.HTTP_200_OK)
