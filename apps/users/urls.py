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
    RetailerProfileUpdateView
)

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('retailer/profile/update/', RetailerProfileUpdateView.as_view(), name='retailer-profile-update'),
    
    # Wholesalers
    path('wholesalers/', WholesalerListView.as_view(), name='wholesaler-list'),
    path('wholesalers/<int:pk>/', WholesalerDetailView.as_view(), name='wholesaler-detail'),
]