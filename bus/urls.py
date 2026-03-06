"""
Bus URLs - API routes for bus endpoints
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusRouteViewSet, BusStopViewSet

router = DefaultRouter()
router.register(r'routes', BusRouteViewSet, basename='route')
router.register(r'stops', BusStopViewSet, basename='stop')

urlpatterns = [
    path('', include(router.urls)),
]
