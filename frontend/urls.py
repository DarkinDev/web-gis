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
    path('profile/', views.profile_view, name='profile'),
    # Management page
    path('management/', views.management_view, name='management'),
    # CRUD API for Routes
    path('mgmt/routes/create/', views.api_create_route, name='api-create-route'),
    path('mgmt/routes/<int:pk>/update/', views.api_update_route, name='api-update-route'),
    path('mgmt/routes/<int:pk>/delete/', views.api_delete_route, name='api-delete-route'),
    path('mgmt/routes/<int:pk>/restore/', views.api_restore_route, name='api-restore-route'),
    path('mgmt/routes/<int:pk>/get/', views.api_get_route, name='api-get-route'),
    # CRUD API for Stops
    path('mgmt/stops/create/', views.api_create_stop, name='api-create-stop'),
    path('mgmt/stops/<int:pk>/update/', views.api_update_stop, name='api-update-stop'),
    path('mgmt/stops/<int:pk>/delete/', views.api_delete_stop, name='api-delete-stop'),
    path('mgmt/stops/<int:pk>/restore/', views.api_restore_stop, name='api-restore-stop'),
    path('mgmt/stops/<int:pk>/get/', views.api_get_stop, name='api-get-stop'),
]
