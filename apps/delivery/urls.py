from django.urls import path
from .views import DeliveryViewSet

urlpatterns = [
    path(
        '',
        DeliveryViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='delivery-list',
    ),
    path(
        '<int:pk>/',
        DeliveryViewSet.as_view(
            {
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy',
            }
        ),
        name='delivery-detail',
    ),
]
