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
    center_metric = center_point.transform(3857, clone=True)
    buffer_metric = center_metric.buffer(radius_meters)
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
    stops = (
        BusStop.objects
        .filter(is_active=True)
        .filter(location__distance_lte=(center_point, D(m=radius_meters)))
        .annotate(distance=Distance('location', center_point))
        .order_by('distance')
    )
    return stops


# ─── Route Finder ─────────────────────────────────────────────────────────────

def _stop_info(stop_id):
    """Helper: return dict of stop info by ID"""
    from bus.models import BusStop
    try:
        s = BusStop.objects.get(pk=stop_id)
        return {'id': s.id, 'name': s.name, 'lat': s.latitude, 'lng': s.longitude}
    except BusStop.DoesNotExist:
        return None


def _find_nearest_routed_stop(stop_id, max_radius_m=3000):
    """
    Khi trạm stop_id không thuộc tuyến nào (không có RouteStop),
    tìm trạm gần nhất CÓ tuyến trong bán kính max_radius_m.
    Returns: (substitute_stop_id, substitute_stop_info) or (None, None)
    """
    from bus.models import BusStop, RouteStop
    from django.contrib.gis.db.models.functions import Distance
    from django.contrib.gis.measure import D

    try:
        origin = BusStop.objects.get(pk=stop_id)
    except BusStop.DoesNotExist:
        return None, None

    # IDs of stops that have at least one RouteStop entry
    routed_stop_ids = set(
        RouteStop.objects.values_list('stop_id', flat=True).distinct()
    )

    # Find nearest active stop that is in routed_stop_ids
    candidates = (
        BusStop.objects
        .filter(is_active=True, id__in=routed_stop_ids)
        .filter(location__distance_lte=(origin.location, D(m=max_radius_m)))
        .annotate(dist=Distance('location', origin.location))
        .order_by('dist')[:1]
    )

    if candidates:
        sub = candidates[0]
        return sub.id, {
            'id': sub.id,
            'name': sub.name,
            'lat': sub.latitude,
            'lng': sub.longitude,
            'distance_m': round(sub.dist.m, 0),
            'is_substitute': True,
            'original_stop_id': stop_id,
            'original_stop_name': origin.name,
        }
    return None, None


def _stops_sequence(route_id, from_stop_id, to_stop_id):
    """Return ordered list of stop dicts from from_stop to to_stop on a route"""
    from bus.models import RouteStop
    try:
        from_order = RouteStop.objects.get(route_id=route_id, stop_id=from_stop_id).order
        to_order   = RouteStop.objects.get(route_id=route_id, stop_id=to_stop_id).order
    except RouteStop.DoesNotExist:
        return []

    if from_order <= to_order:
        qs = RouteStop.objects.filter(
            route_id=route_id, order__gte=from_order, order__lte=to_order
        ).order_by('order')
    else:
        qs = RouteStop.objects.filter(
            route_id=route_id, order__gte=to_order, order__lte=from_order
        ).order_by('-order')

    return [
        {'name': rs.stop.name, 'lat': rs.stop.latitude, 'lng': rs.stop.longitude, 'order': rs.order}
        for rs in qs.select_related('stop')
    ]


def get_route_between_stops(start_stop_id, end_stop_id):
    """
    Find routes that connect two stops.
    If a stop has no RouteStop entries, substitute the nearest routed stop.
    Returns: (results_list, substitution_info_dict)
    """
    from bus.models import RouteStop, BusRoute

    substitutions = {}

    # Check if start stop has routes; if not, find nearest substitute
    start_routes = set(RouteStop.objects.filter(stop_id=start_stop_id).values_list('route_id', flat=True))
    if not start_routes:
        sub_id, sub_info = _find_nearest_routed_stop(start_stop_id)
        if sub_id:
            substitutions['start'] = sub_info
            start_stop_id = sub_id
            start_routes = set(RouteStop.objects.filter(stop_id=sub_id).values_list('route_id', flat=True))

    # Check if end stop has routes; if not, find nearest substitute
    end_routes = set(RouteStop.objects.filter(stop_id=end_stop_id).values_list('route_id', flat=True))
    if not end_routes:
        sub_id, sub_info = _find_nearest_routed_stop(end_stop_id)
        if sub_id:
            substitutions['end'] = sub_info
            end_stop_id = sub_id
            end_routes = set(RouteStop.objects.filter(stop_id=sub_id).values_list('route_id', flat=True))

    results = []

    # ─── 1. Direct Routes ────────────────────────────────────────────────────
    direct_ids = start_routes & end_routes
    for route_id in direct_ids:
        route = BusRoute.objects.get(id=route_id)
        seq   = _stops_sequence(route_id, start_stop_id, end_stop_id)
        results.append({
            'type':        'direct',
            'route_id':    route.id,
            'route_number': route.route_number,
            'route_name':  route.name,
            'color':       route.color,
            'stops':       seq,
            'total_stops': len(seq),
        })

    if results:
        return results, substitutions

    # ─── 2. 1-Transfer Routes ────────────────────────────────────────────────
    # Build: stop_id → frozenset(route_ids) for all active routes
    all_rs = RouteStop.objects.select_related('stop').values_list('stop_id', 'route_id')
    stop_to_routes = {}
    route_to_stops = {}
    for stop_id, route_id in all_rs:
        stop_to_routes.setdefault(stop_id, set()).add(route_id)
        route_to_stops.setdefault(route_id, set()).add(stop_id)

    seen_transfers = set()

    for s_route_id in start_routes:
        s_route = BusRoute.objects.get(id=s_route_id)
        # All stops reachable from start via this route
        for mid_stop_id in route_to_stops.get(s_route_id, set()):
            if mid_stop_id == start_stop_id:
                continue
            # Which routes go through mid_stop AND reach end_stop?
            mid_routes = stop_to_routes.get(mid_stop_id, set())
            common = mid_routes & end_routes
            for e_route_id in common:
                if e_route_id == s_route_id:
                    continue  # same route → not a real transfer
                key = (s_route_id, mid_stop_id, e_route_id)
                if key in seen_transfers:
                    continue
                seen_transfers.add(key)

                e_route  = BusRoute.objects.get(id=e_route_id)
                mid_stop = _stop_info(mid_stop_id)

                seg1 = _stops_sequence(s_route_id, start_stop_id, mid_stop_id)
                seg2 = _stops_sequence(e_route_id, mid_stop_id, end_stop_id)

                results.append({
                    'type': 'transfer',
                    'transfer_stop': mid_stop,
                    'segments': [
                        {
                            'route_id':     s_route.id,
                            'route_number': s_route.route_number,
                            'route_name':   s_route.name,
                            'color':        s_route.color,
                            'stops':        seg1,
                            'total_stops':  len(seg1),
                            'from_stop':    start_stop_id,
                            'to_stop':      mid_stop_id,
                        },
                        {
                            'route_id':     e_route.id,
                            'route_number': e_route.route_number,
                            'route_name':   e_route.name,
                            'color':        e_route.color,
                            'stops':        seg2,
                            'total_stops':  len(seg2),
                            'from_stop':    mid_stop_id,
                            'to_stop':      end_stop_id,
                        },
                    ],
                })
                if len(results) >= 4:
                    return results, substitutions  # limit 1-transfer options

    if results:
        return results, substitutions

    # ─── 3. 2-Transfer Routes (BFS depth-2) ─────────────────────────────────
    seen_2 = set()

    for s_route_id in start_routes:
        s_route = BusRoute.objects.get(id=s_route_id)
        for mid1_stop_id in route_to_stops.get(s_route_id, set()):
            if mid1_stop_id == start_stop_id:
                continue
            for m1_route_id in stop_to_routes.get(mid1_stop_id, set()):
                if m1_route_id == s_route_id:
                    continue
                m1_route = BusRoute.objects.get(id=m1_route_id)
                for mid2_stop_id in route_to_stops.get(m1_route_id, set()):
                    if mid2_stop_id in (start_stop_id, mid1_stop_id):
                        continue
                    common2 = stop_to_routes.get(mid2_stop_id, set()) & end_routes
                    for e_route_id in common2:
                        if e_route_id in (s_route_id, m1_route_id):
                            continue
                        key2 = (s_route_id, mid1_stop_id, m1_route_id, mid2_stop_id, e_route_id)
                        if key2 in seen_2:
                            continue
                        seen_2.add(key2)

                        e_route   = BusRoute.objects.get(id=e_route_id)
                        mid1_stop = _stop_info(mid1_stop_id)
                        mid2_stop = _stop_info(mid2_stop_id)

                        seg1 = _stops_sequence(s_route_id,  start_stop_id, mid1_stop_id)
                        seg2 = _stops_sequence(m1_route_id, mid1_stop_id,  mid2_stop_id)
                        seg3 = _stops_sequence(e_route_id,  mid2_stop_id,  end_stop_id)

                        results.append({
                            'type': 'transfer2',
                            'transfer_stops': [mid1_stop, mid2_stop],
                            'segments': [
                                {
                                    'route_id':     s_route.id,
                                    'route_number': s_route.route_number,
                                    'route_name':   s_route.name,
                                    'color':        s_route.color,
                                    'stops':        seg1,
                                    'total_stops':  len(seg1),
                                },
                                {
                                    'route_id':     m1_route.id,
                                    'route_number': m1_route.route_number,
                                    'route_name':   m1_route.name,
                                    'color':        m1_route.color,
                                    'stops':        seg2,
                                    'total_stops':  len(seg2),
                                },
                                {
                                    'route_id':     e_route.id,
                                    'route_number': e_route.route_number,
                                    'route_name':   e_route.name,
                                    'color':        e_route.color,
                                    'stops':        seg3,
                                    'total_stops':  len(seg3),
                                },
                            ],
                        })
                        if len(results) >= 3:
                            return results, substitutions

    return results, substitutions
