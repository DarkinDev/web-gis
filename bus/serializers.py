"""
Bus Serializers - REST API serializers for bus models
"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import BusRoute, BusStop, RouteStop


class BusStopSerializer(serializers.ModelSerializer):
    """Basic serializer for BusStop"""
    routes = serializers.SerializerMethodField()
    
    class Meta:
        model = BusStop
        fields = [
            'id', 'name', 'code', 'address', 
            'latitude', 'longitude',
            'has_shelter', 'has_bench', 'is_active',
            'routes'
        ]
    
    def get_routes(self, obj):
        routes = obj.get_routes()
        return [{'id': r.id, 'route_number': r.route_number, 'name': r.name} for r in routes]


class BusStopGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for BusStop"""
    routes = serializers.SerializerMethodField()
    
    class Meta:
        model = BusStop
        geo_field = 'location'
        fields = [
            'id', 'name', 'code', 'address',
            'has_shelter', 'has_bench', 'is_active',
            'routes'
        ]
    
    def get_routes(self, obj):
        routes = obj.get_routes()
        return [{'id': r.id, 'route_number': r.route_number, 'name': r.name, 'color': r.color} for r in routes]


class RouteStopSerializer(serializers.ModelSerializer):
    """Serializer for RouteStop with stop details"""
    stop_name = serializers.CharField(source='stop.name', read_only=True)
    stop_address = serializers.CharField(source='stop.address', read_only=True)
    latitude = serializers.FloatField(source='stop.latitude', read_only=True)
    longitude = serializers.FloatField(source='stop.longitude', read_only=True)
    
    class Meta:
        model = RouteStop
        fields = [
            'id', 'order', 'stop_name', 'stop_address',
            'latitude', 'longitude',
            'distance_from_start', 'estimated_time'
        ]


class BusRouteSerializer(serializers.ModelSerializer):
    """Basic serializer for BusRoute"""
    stops = serializers.SerializerMethodField()
    
    class Meta:
        model = BusRoute
        fields = [
            'id', 'route_number', 'name', 'description',
            'start_point', 'end_point',
            'operating_hours', 'frequency', 'ticket_price',
            'color', 'total_stops', 'is_active',
            'stops'
        ]
    
    def get_stops(self, obj):
        route_stops = RouteStop.objects.filter(route=obj).order_by('order')
        return RouteStopSerializer(route_stops, many=True).data


class BusRouteGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for BusRoute"""
    stops = serializers.SerializerMethodField()
    
    class Meta:
        model = BusRoute
        geo_field = 'geometry'
        fields = [
            'id', 'route_number', 'name', 'description',
            'start_point', 'end_point',
            'operating_hours', 'frequency', 'ticket_price',
            'color', 'total_stops', 'is_active',
            'stops'
        ]
    
    def get_stops(self, obj):
        route_stops = RouteStop.objects.filter(route=obj).order_by('order')
        return RouteStopSerializer(route_stops, many=True).data


class BusRouteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for route list"""
    class Meta:
        model = BusRoute
        fields = ['id', 'route_number', 'name', 'color', 'total_stops', 'is_active']
