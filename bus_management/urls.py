"""
URL configuration for bus_management project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bus.urls')),
    path('api/gis/', include('gis_tools.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password_reset...
    path('', include('frontend.urls')),
]
