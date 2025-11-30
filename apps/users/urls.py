"""
User URLs
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView,
    UserProfileView,
    WholesalerListView,
    WholesalerDetailView
)

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # Wholesalers
    path('wholesalers/', WholesalerListView.as_view(), name='wholesaler-list'),
    path('wholesalers/<int:pk>/', WholesalerDetailView.as_view(), name='wholesaler-detail'),
]