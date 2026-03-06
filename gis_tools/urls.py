"""
GIS Tools URLs - API routes for GIS operations
"""
from django.urls import path
from . import views

urlpatterns = [
    path('distance/', views.calculate_distance_view, name='gis-distance'),
    path('nearest/', views.nearest_stops_view, name='gis-nearest'),
    path('buffer/', views.create_buffer_view, name='gis-buffer'),
    path('check-service-area/', views.check_in_service_area_view, name='gis-check-service'),
    path('stops-in-radius/', views.stops_in_radius_view, name='gis-stops-radius'),
    path('find-route/', views.find_route_view, name='gis-find-route'),
]
