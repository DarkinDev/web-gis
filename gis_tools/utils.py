"""
GIS Utilities - PostGIS spatial operations
"""
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from bus.models import BusStop, BusRoute


def calculate_distance(point1_coords, point2_coords):
    """
    Calculate distance between two points using PostGIS ST_Distance
    
    Args:
        point1_coords: tuple (lng, lat) for first point
        point2_coords: tuple (lng, lat) for second point
    
    Returns:
        Distance in meters
    """
    point1 = Point(point1_coords[0], point1_coords[1], srid=4326)
    point2 = Point(point2_coords[0], point2_coords[1], srid=4326)
    
    # Transform to metric CRS for accurate distance calculation
    point1_metric = point1.transform(3857, clone=True)
    point2_metric = point2.transform(3857, clone=True)
    
    return point1_metric.distance(point2_metric)


def find_nearest_stops(user_location, limit=5):
    """
    Find nearest bus stops using PostGIS nearest neighbor query
    
    Args:
        user_location: Point object or tuple (lng, lat)
        limit: Maximum number of stops to return
    
    Returns:
        QuerySet of BusStop objects with distance annotation
    """
    if isinstance(user_location, tuple):
        user_location = Point(user_location[0], user_location[1], srid=4326)
    
    stops = (
        BusStop.objects
        .filter(is_active=True)
        .annotate(distance=Distance('location', user_location))
        .order_by('distance')[:limit]
    )
    
    return stops


def create_buffer(center_point, radius_meters):
    """
    Create a buffer zone around a point using PostGIS ST_Buffer
    
    Args:
        center_point: Point object or tuple (lng, lat)
        radius_meters: Buffer radius in meters
    
    Returns:
        Polygon geometry representing the buffer
    """
    if isinstance(center_point, tuple):
        center_point = Point(center_point[0], center_point[1], srid=4326)
    
    # Transform to metric CRS, create buffer, transform back to WGS84
    center_metric = center_point.transform(3857, clone=True)
    buffer_metric = center_metric.buffer(radius_meters)
    
    # Transform back to WGS84
    buffer_wgs84 = GEOSGeometry(buffer_metric.wkt, srid=3857)
    buffer_wgs84.transform(4326)
    
    return buffer_wgs84


def check_point_in_buffer(point, buffer_polygon):
    """
    Check if a point is within a buffer zone using PostGIS ST_Contains
    
    Args:
        point: Point object or tuple (lng, lat)
        buffer_polygon: Polygon geometry
    
    Returns:
        Boolean indicating if point is within buffer
    """
    if isinstance(point, tuple):
        point = Point(point[0], point[1], srid=4326)
    
    return buffer_polygon.contains(point)


def find_stops_in_buffer(center_point, radius_meters):
    """
    Find all bus stops within a buffer zone
    
    Args:
        center_point: Point object or tuple (lng, lat)
        radius_meters: Search radius in meters
    
    Returns:
        QuerySet of BusStop objects within the buffer
    """
    if isinstance(center_point, tuple):
        center_point = Point(center_point[0], center_point[1], srid=4326)
    
    stops = (
        BusStop.objects
        .filter(is_active=True)
        .filter(location__distance_lte=(center_point, D(m=radius_meters)))
        .annotate(distance=Distance('location', center_point))
        .order_by('distance')
    )
    
    return stops


def get_route_between_stops(start_stop_id, end_stop_id):
    """
    Find routes that connect two stops and return the path
    
    Args:
        start_stop_id: ID of starting stop
        end_stop_id: ID of ending stop
    
    Returns:
        List of dicts with route info and stop sequence
    """
    from bus.models import RouteStop
    
    # Find routes that contain both stops
    start_routes = set(RouteStop.objects.filter(stop_id=start_stop_id).values_list('route_id', flat=True))
    end_routes = set(RouteStop.objects.filter(stop_id=end_stop_id).values_list('route_id', flat=True))
    
    common_routes = start_routes.intersection(end_routes)
    
    results = []
    for route_id in common_routes:
        route = BusRoute.objects.get(id=route_id)
        
        # Get stop sequence
        start_order = RouteStop.objects.get(route_id=route_id, stop_id=start_stop_id).order
        end_order = RouteStop.objects.get(route_id=route_id, stop_id=end_stop_id).order
        
        if start_order < end_order:
            route_stops = (
                RouteStop.objects
                .filter(route_id=route_id, order__gte=start_order, order__lte=end_order)
                .order_by('order')
                .select_related('stop')
            )
        else:
            route_stops = (
                RouteStop.objects
                .filter(route_id=route_id, order__gte=end_order, order__lte=start_order)
                .order_by('-order')
                .select_related('stop')
            )
        
        stops_sequence = [
            {
                'name': rs.stop.name,
                'lat': rs.stop.latitude,
                'lng': rs.stop.longitude,
                'order': rs.order
            }
            for rs in route_stops
        ]
        
        results.append({
            'route_id': route.id,
            'route_number': route.route_number,
            'route_name': route.name,
            'color': route.color,
            'stops': stops_sequence,
            'total_stops': len(stops_sequence)
        })
    
    return results
