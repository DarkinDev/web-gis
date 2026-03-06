"""
GIS Tools Views - API endpoints for GIS operations
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.geos import Point
from .utils import (
    calculate_distance,
    find_nearest_stops,
    create_buffer,
    check_point_in_buffer,
    find_stops_in_buffer,
    get_route_between_stops
)
from bus.serializers import BusStopSerializer


@api_view(['GET'])
def calculate_distance_view(request):
    """
    Calculate distance between two points
    
    Query params:
        lng1, lat1: First point coordinates
        lng2, lat2: Second point coordinates
    
    Returns:
        Distance in meters and kilometers
    """
    try:
        lng1 = float(request.query_params.get('lng1'))
        lat1 = float(request.query_params.get('lat1'))
        lng2 = float(request.query_params.get('lng2'))
        lat2 = float(request.query_params.get('lat2'))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Yêu cầu các tham số: lng1, lat1, lng2, lat2'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    distance_meters = calculate_distance((lng1, lat1), (lng2, lat2))
    
    return Response({
        'distance_meters': round(distance_meters, 2),
        'distance_km': round(distance_meters / 1000, 3),
        'point1': {'lng': lng1, 'lat': lat1},
        'point2': {'lng': lng2, 'lat': lat2}
    })


@api_view(['GET'])
def nearest_stops_view(request):
    """
    Find nearest bus stops to a given location
    
    Query params:
        lng, lat: User location coordinates
        limit: Maximum number of stops (default: 5)
    
    Returns:
        List of nearest stops with distances
    """
    try:
        lng = float(request.query_params.get('lng'))
        lat = float(request.query_params.get('lat'))
        limit = int(request.query_params.get('limit', 5))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Yêu cầu các tham số: lng, lat'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stops = find_nearest_stops((lng, lat), limit)
    
    result = []
    for stop in stops:
        data = BusStopSerializer(stop).data
        data['distance_meters'] = round(stop.distance.m, 2)
        data['distance_km'] = round(stop.distance.m / 1000, 3)
        result.append(data)
    
    return Response({
        'user_location': {'lng': lng, 'lat': lat},
        'nearest_stops': result
    })


@api_view(['GET'])
def create_buffer_view(request):
    """
    Create a buffer zone around a point
    
    Query params:
        lng, lat: Center point coordinates
        radius: Buffer radius in meters (default: 500)
    
    Returns:
        GeoJSON polygon of the buffer zone
    """
    try:
        lng = float(request.query_params.get('lng'))
        lat = float(request.query_params.get('lat'))
        radius = float(request.query_params.get('radius', 500))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Yêu cầu các tham số: lng, lat'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    buffer_polygon = create_buffer((lng, lat), radius)
    
    import json
    return Response({
        'type': 'Feature',
        'properties': {
            'center': {'lng': lng, 'lat': lat},
            'radius_meters': radius
        },
        'geometry': json.loads(buffer_polygon.json)
    })


@api_view(['GET'])
def check_in_service_area_view(request):
    """
    Check if a point is within a service area (buffer around a stop)
    
    Query params:
        stop_id: Bus stop ID
        lng, lat: Point to check
        radius: Service area radius in meters (default: 500)
    
    Returns:
        Boolean indicating if point is in service area
    """
    try:
        stop_id = int(request.query_params.get('stop_id'))
        lng = float(request.query_params.get('lng'))
        lat = float(request.query_params.get('lat'))
        radius = float(request.query_params.get('radius', 500))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Yêu cầu các tham số: stop_id, lng, lat'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from bus.models import BusStop
    try:
        stop = BusStop.objects.get(id=stop_id)
    except BusStop.DoesNotExist:
        return Response(
            {'error': 'Không tìm thấy trạm dừng'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    buffer_polygon = create_buffer(stop.location, radius)
    point = Point(lng, lat, srid=4326)
    is_in_area = check_point_in_buffer(point, buffer_polygon)
    
    return Response({
        'stop': {
            'id': stop.id,
            'name': stop.name,
            'lng': stop.longitude,
            'lat': stop.latitude
        },
        'check_point': {'lng': lng, 'lat': lat},
        'radius_meters': radius,
        'is_in_service_area': is_in_area
    })


@api_view(['GET'])
def stops_in_radius_view(request):
    """
    Find all stops within a radius of a point
    
    Query params:
        lng, lat: Center point coordinates
        radius: Search radius in meters (default: 500)
    
    Returns:
        List of stops within the radius with distances
    """
    try:
        lng = float(request.query_params.get('lng'))
        lat = float(request.query_params.get('lat'))
        radius = float(request.query_params.get('radius', 500))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Yêu cầu các tham số: lng, lat'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stops = find_stops_in_buffer((lng, lat), radius)
    
    result = []
    for stop in stops:
        data = BusStopSerializer(stop).data
        data['distance_meters'] = round(stop.distance.m, 2)
        result.append(data)
    
    # Also return buffer geometry for display
    buffer_polygon = create_buffer((lng, lat), radius)
    import json
    
    return Response({
        'center': {'lng': lng, 'lat': lat},
        'radius_meters': radius,
        'stops_count': len(result),
        'stops': result,
        'buffer_geojson': {
            'type': 'Feature',
            'properties': {},
            'geometry': json.loads(buffer_polygon.json)
        }
    })


@api_view(['GET'])
def find_route_view(request):
    """
    Find routes between two stops
    
    Query params:
        start_stop_id: Starting stop ID
        end_stop_id: Ending stop ID
    
    Returns:
        List of routes connecting the two stops
    """
    try:
        start_stop_id = int(request.query_params.get('start_stop_id'))
        end_stop_id = int(request.query_params.get('end_stop_id'))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Yêu cầu các tham số: start_stop_id, end_stop_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from bus.models import BusStop
    try:
        start_stop = BusStop.objects.get(id=start_stop_id)
        end_stop = BusStop.objects.get(id=end_stop_id)
    except BusStop.DoesNotExist:
        return Response(
            {'error': 'Không tìm thấy trạm dừng'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    routes = get_route_between_stops(start_stop_id, end_stop_id)
    
    return Response({
        'start_stop': {
            'id': start_stop.id,
            'name': start_stop.name,
            'lat': start_stop.latitude,
            'lng': start_stop.longitude
        },
        'end_stop': {
            'id': end_stop.id,
            'name': end_stop.name,
            'lat': end_stop.latitude,
            'lng': end_stop.longitude
        },
        'routes_found': len(routes),
        'routes': routes
    })
