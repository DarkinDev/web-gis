"""
Frontend URLs - User-facing routes
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public pages - Landing là trang chủ mặc định
    path('', views.landing_view, name='landing'),
    path('map/', views.home_view, name='home'),
    path('routes/', views.routes_list_view, name='routes-list'),
    path('routes/<int:pk>/', views.route_detail_view, name='route-detail'),
    path('stops/', views.stops_list_view, name='stops-list'),
    path('stops/<int:pk>/', views.stop_detail_view, name='stop-detail'),
    path('profile/', views.profile_view, name='profile'),

    # Management page
    path('management/', views.management_view, name='management'),
    path('management/users/', views.user_management_view, name='user-management'),
    
    # User Management API
    path('mgmt/users/<int:user_id>/toggle-status/', views.api_toggle_user_status, name='api-toggle-user-status'),
    path('mgmt/users/<int:user_id>/toggle-staff/', views.api_toggle_user_staff, name='api-toggle-user-staff'),
    path('mgmt/users/<int:user_id>/update-email/', views.api_update_user_email, name='api-update-user-email'),
    path('mgmt/users/<int:user_id>/reset-password/', views.api_reset_user_password, name='api-reset-user-password'),
    path('mgmt/users/<int:user_id>/delete/', views.api_delete_user, name='api-delete-user'),

    # CRUD API for Routes
    path('mgmt/routes/create/',                          views.api_create_route,       name='api-create-route'),
    path('mgmt/routes/<int:pk>/update/',                 views.api_update_route,       name='api-update-route'),
    path('mgmt/routes/<int:pk>/delete/',                 views.api_delete_route,       name='api-delete-route'),
    path('mgmt/routes/<int:pk>/restore/',                views.api_restore_route,      name='api-restore-route'),
    path('mgmt/routes/<int:pk>/get/',                    views.api_get_route,          name='api-get-route'),

    # Route ↔ Stop management
    path('mgmt/routes/<int:pk>/stops/',                  views.api_get_route_stops,    name='api-route-stops'),
    path('mgmt/routes/<int:pk>/stops/add/',              views.api_add_route_stop,     name='api-add-route-stop'),
    path('mgmt/routes/<int:pk>/stops/<int:rs_id>/remove/', views.api_remove_route_stop, name='api-remove-route-stop'),
    path('mgmt/routes/<int:pk>/stops/reorder/',          views.api_reorder_route_stops, name='api-reorder-route-stops'),

    # CRUD API for Stops
    path('mgmt/stops/create/',              views.api_create_stop,   name='api-create-stop'),
    path('mgmt/stops/<int:pk>/update/',     views.api_update_stop,   name='api-update-stop'),
    path('mgmt/stops/<int:pk>/delete/',     views.api_delete_stop,   name='api-delete-stop'),
    path('mgmt/stops/<int:pk>/restore/',    views.api_restore_stop,  name='api-restore-stop'),
    path('mgmt/stops/<int:pk>/get/',        views.api_get_stop,      name='api-get-stop'),

    # Excel Export
    path('mgmt/export/users.xlsx',             views.export_users_excel,  name='export-users-excel'),
    path('mgmt/export/stops/tram_dung.xlsx',   views.export_stops_excel,  name='export-stops-excel'),
    path('mgmt/export/routes/tuyen_xe.xlsx',   views.export_routes_excel, name='export-routes-excel'),
    path('mgmt/export/routes/<int:pk>/stops.xlsx', views.export_route_stops_excel, name='export-route-stops-excel'),

    # Excel Import
    path('mgmt/import/stops/',   views.import_stops_excel,  name='import-stops-excel'),
    path('mgmt/import/routes/',  views.import_routes_excel, name='import-routes-excel'),
]
