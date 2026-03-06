"""
Frontend URLs - User-facing routes
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('routes/', views.routes_list_view, name='routes-list'),
    path('routes/<int:pk>/', views.route_detail_view, name='route-detail'),
    path('stops/', views.stops_list_view, name='stops-list'),
]
