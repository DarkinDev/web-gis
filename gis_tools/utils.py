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
    """
    point1 = Point(point1_coords[0], point1_coords[1], srid=4326)
    point2 = Point(point2_coords[0], point2_coords[1], srid=4326)
    
    # Use geodetic distance (spheroid) for accurate meters without transformation
    # Or transform to a local projection. 3857 is okay for small distances.
    p1_metric = point1.transform(3857, clone=True)
    p2_metric = point2.transform(3857, clone=True)
    
    return p1_metric.distance(p2_metric)


def find_nearest_stops(user_location, limit=5):
    """
    Find nearest bus stops using PostGIS nearest neighbor query
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
    Create a buffer zone around a point
    """
    if isinstance(center_point, tuple):
        center_point = Point(center_point[0], center_point[1], srid=4326)
    
    # PostGIS ST_Buffer on geography or transform to metric
    # For simplicity and accuracy in meters, transform to 3857 (Web Mercator)
    center_metric = center_point.transform(3857, clone=True)
    buffer_metric = center_metric.buffer(radius_meters)
    
    # Transform back to 4326
    buffer_wgs84 = buffer_metric.transform(4326, clone=True)
    
    return buffer_wgs84


def check_point_in_buffer(point, buffer_polygon):
    """
    Check if a point is within a buffer zone
    """
    if isinstance(point, tuple):
        point = Point(point[0], point[1], srid=4326)
    
    return buffer_polygon.contains(point)


def find_stops_in_buffer(center_point, radius_meters):
    """
    Find all bus stops within a buffer zone
    """
    if isinstance(center_point, tuple):
        center_point = Point(center_point[0], center_point[1], srid=4326)
    
    # Use dwithin for performance if possible, or distance_lte
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
    Find routes that connect two stops (direct or with 1 transfer)
    """
    from bus.models import RouteStop, BusRoute
    import json
    
    # 1. Direct Routes
    start_routes = set(RouteStop.objects.filter(stop_id=start_stop_id).values_list('route_id', flat=True))
    end_routes = set(RouteStop.objects.filter(stop_id=end_stop_id).values_list('route_id', flat=True))
    
    direct_route_ids = start_routes.intersection(end_routes)
    results = []
    
    for route_id in direct_route_ids:
        route = BusRoute.objects.get(id=route_id)
        start_order = RouteStop.objects.get(route_id=route_id, stop_id=start_stop_id).order
        end_order = RouteStop.objects.get(route_id=route_id, stop_id=end_stop_id).order
        
        # Determine direction
        if start_order < end_order:
            stops_qs = RouteStop.objects.filter(route_id=route_id, order__gte=start_order, order__lte=end_order).order_by('order')
        else:
            stops_qs = RouteStop.objects.filter(route_id=route_id, order__gte=end_order, order__lte=start_order).order_by('-order')
            
        stops_sequence = [{'name': rs.stop.name, 'lat': rs.stop.latitude, 'lng': rs.stop.longitude, 'order': rs.order} for rs in stops_qs.select_related('stop')]
        
        results.append({
            'type': 'direct',
            'route_id': route.id,
            'route_number': route.route_number,
            'route_name': route.name,
            'color': route.color,
            'stops': stops_sequence,
            'total_stops': len(stops_sequence)
        })

    # 2. 1-Transfer Routes (Only if no direct routes found or as additional options)
    if not results:
        # This is a basic implementation of 1-transfer
        # Find all routes from start_stop
        for s_route_id in start_routes:
            s_route = BusRoute.objects.get(id=s_route_id)
            s_stop_order = RouteStop.objects.get(route_id=s_route_id, stop_id=start_stop_id).order
            
            # Get all stops on this route AFTER the start_stop
            s_route_stops = RouteStop.objects.filter(route_id=s_route_id, order__gt=s_stop_order).values_list('stop_id', flat=True)
            
            # Check if any of these stops are on a route that goes to end_stop
            for transfer_stop_id in s_route_stops:
                transfer_routes = set(RouteStop.objects.filter(stop_id=transfer_stop_id).values_list('route_id', flat=True))
                common_end_routes = transfer_routes.intersection(end_routes)
                
                if common_end_routes:
                    # Found a transfer! (Taking the first common end route for brevity)
                    e_route_id = list(common_end_routes)[0]
                    e_route = BusRoute.objects.get(id=e_route_id)
                    
                    t_stop_obj = BusStop.objects.get(id=transfer_stop_id)
                    
                    # Construct transfer info
                    results.append({
                        'type': 'transfer',
                        'transfer_stop': {'id': t_stop_obj.id, 'name': t_stop_obj.name, 'lat': t_stop_obj.latitude, 'lng': t_stop_obj.longitude},
                        'segments': [
                            {
                                'route_number': s_route.route_number,
                                'route_name': s_route.name,
                                'color': s_route.color,
                                'from_stop': start_stop_id,
                                'to_stop': transfer_stop_id
                            },
                            {
                                'route_number': e_route.route_number,
                                'route_name': e_route.name,
                                'color': e_route.color,
                                'from_stop': transfer_stop_id,
                                'to_stop': end_stop_id
                            }
                        ]
                    })
                    if len(results) >= 3: break # Limit to 3 transfer options
            if len(results) >= 3: break

    return results
