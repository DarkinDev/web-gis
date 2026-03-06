"""
Bus Views - API views for bus management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import BusRoute, BusStop, RouteStop
from .serializers import (
    BusRouteSerializer, BusRouteGeoSerializer, BusRouteListSerializer,
    BusStopSerializer, BusStopGeoSerializer
)


class BusRouteViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for BusRoute"""
    queryset = BusRoute.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'route_number', 'description']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BusRouteListSerializer
        if self.request.query_params.get('format') == 'geojson':
            return BusRouteGeoSerializer
        return BusRouteSerializer
    
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """Get all routes as GeoJSON"""
        queryset = self.get_queryset().exclude(geometry__isnull=True)
        serializer = BusRouteGeoSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stops(self, request, pk=None):
        """Get all stops for a specific route"""
        route = self.get_object()
        route_stops = RouteStop.objects.filter(route=route).order_by('order')
        stops = [rs.stop for rs in route_stops]
        serializer = BusStopSerializer(stops, many=True)
        return Response(serializer.data)


class BusStopViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for BusStop"""
    queryset = BusStop.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'address']
    
    def get_serializer_class(self):
        if self.request.query_params.get('format') == 'geojson':
            return BusStopGeoSerializer
        return BusStopSerializer
    
    @action(detail=False, methods=['get'])
    def geojson(self, request):
        """Get all stops as GeoJSON"""
        queryset = self.get_queryset()
        serializer = BusStopGeoSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search stops by name"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'error': 'Query must be at least 2 characters'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        stops = self.get_queryset().filter(name__icontains=query)[:20]
        serializer = BusStopSerializer(stops, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nearest(self, request):
        """Find nearest stops to a given location"""
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            limit = int(request.query_params.get('limit', 5))
        except (TypeError, ValueError):
            return Response(
                {'error': 'Valid lat, lng parameters required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_location = Point(lng, lat, srid=4326)
        stops = (
            self.get_queryset()
            .annotate(distance=Distance('location', user_location))
            .order_by('distance')[:limit]
        )
        
        result = []
        for stop in stops:
            data = BusStopSerializer(stop).data
            data['distance_meters'] = round(stop.distance.m, 2)
            result.append(data)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def by_route(self, request):
        """Get stops for a specific route"""
        route_id = request.query_params.get('route_id')
        if not route_id:
            return Response(
                {'error': 'route_id parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        route_stops = RouteStop.objects.filter(
            route_id=route_id
        ).order_by('order').select_related('stop')
        
        stops = [rs.stop for rs in route_stops]
        serializer = BusStopGeoSerializer(stops, many=True)
        return Response(serializer.data)
