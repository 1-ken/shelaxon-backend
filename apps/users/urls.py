"""
User URLs
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    WholesalerListView,
    WholesalerDetailView,
    ProfileUpdateView,
    AdminPasswordResetView,
    ChangePasswordView,
    AdminUserListView,
    AdminUserDetailView,
)

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('password/change/', ChangePasswordView.as_view(), name='change-password'),
    
    # Wholesalers
    path('wholesalers/', WholesalerListView.as_view(), name='wholesaler-list'),
    path('wholesalers/<int:pk>/', WholesalerDetailView.as_view(), name='wholesaler-detail'),
    
    # Admin endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/password-reset/', AdminPasswordResetView.as_view(), name='admin-password-reset'),
]