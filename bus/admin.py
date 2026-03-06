"""
Bus Admin - Django Admin configuration for bus models
"""
from django.contrib.gis import admin
from django.contrib.gis.admin import GISModelAdmin
from leaflet.admin import LeafletGeoAdmin
from .models import BusRoute, BusStop, RouteStop


class RouteStopInline(admin.TabularInline):
    """Inline admin for RouteStop"""
    model = RouteStop
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['stop']


@admin.register(BusRoute)
class BusRouteAdmin(LeafletGeoAdmin):
    """Admin for BusRoute model"""
    list_display = [
        'route_number', 
        'name', 
        'start_point', 
        'end_point', 
        'operating_hours',
        'ticket_price',
        'total_stops',
        'is_active'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['route_number', 'name', 'start_point', 'end_point']
    ordering = ['route_number']
    inlines = [RouteStopInline]
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('route_number', 'name', 'description')
        }),
        ('Lộ trình', {
            'fields': ('start_point', 'end_point', 'geometry')
        }),
        ('Thông tin hoạt động', {
            'fields': ('operating_hours', 'frequency', 'ticket_price')
        }),
        ('Hiển thị', {
            'fields': ('color', 'is_active')
        }),
    )


@admin.register(BusStop)
class BusStopAdmin(LeafletGeoAdmin):
    """Admin for BusStop model with map widget"""
    list_display = [
        'name', 
        'code', 
        'address', 
        'has_shelter', 
        'has_bench',
        'is_active',
        'get_routes_display'
    ]
    list_filter = ['is_active', 'has_shelter', 'has_bench']
    search_fields = ['name', 'code', 'address']
    ordering = ['name']
    
    fieldsets = (
        ('Thông tin trạm', {
            'fields': ('name', 'code', 'address')
        }),
        ('Vị trí', {
            'fields': ('location',)
        }),
        ('Tiện ích', {
            'fields': ('has_shelter', 'has_bench', 'is_active')
        }),
    )

    def get_routes_display(self, obj):
        routes = obj.get_routes()
        return ', '.join([r.route_number for r in routes[:5]])
    get_routes_display.short_description = 'Tuyến đi qua'


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    """Admin for RouteStop model"""
    list_display = ['route', 'stop', 'order', 'distance_from_start', 'estimated_time']
    list_filter = ['route']
    search_fields = ['route__route_number', 'stop__name']
    ordering = ['route', 'order']
    autocomplete_fields = ['route', 'stop']
