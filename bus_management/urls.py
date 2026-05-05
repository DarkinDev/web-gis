"""
URL configuration for bus_management project.
"""
from django.contrib import admin
from django.urls import path, include
from frontend import views as frontend_views

# Đổi giao diện Admin thành Hệ quản lý BusGIS
admin.site.site_header = "Hệ quản lý BusGIS"
admin.site.site_title = "Quản lý BusGIS"
admin.site.index_title = "Bảng điều khiển BusGIS"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bus.urls')),
    path('api/gis/', include('gis_tools.urls')),
    path('accounts/register/', frontend_views.register_view, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password_reset...
    path('', include('frontend.urls')),
]
