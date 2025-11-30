from django.urls import path
from .views import AnalyticsOverview

urlpatterns = [
    path('overview/', AnalyticsOverview.as_view(), name='analytics-overview'),
]
