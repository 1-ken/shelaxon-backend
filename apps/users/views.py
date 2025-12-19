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
    CustomTokenObtainPairSerializer,
)
from .models import WholesalerProfile

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