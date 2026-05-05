import os, sys, io, django
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bus_management.settings'
django.setup()

from bus.models import BusStop, BusRoute, RouteStop

# Check stop 3467 (Ben xe Cu Chi) and stop 401 (Cho Ben Thanh)
for sid in [3467, 401]:
    try:
        stop = BusStop.objects.get(pk=sid)
        routes = RouteStop.objects.filter(stop=stop).select_related('route')
        print(f"\nStop {sid}: {stop.name}")
        print(f"  Routes passing through ({routes.count()}):")
        for rs in routes:
            print(f"    Route {rs.route.route_number}: {rs.route.name} (order={rs.order})")
    except BusStop.DoesNotExist:
        print(f"\nStop {sid}: NOT FOUND")

# Also check total RouteStop count
total_rs = RouteStop.objects.count()
total_routes_with_stops = RouteStop.objects.values('route_id').distinct().count()
total_stops_with_routes = RouteStop.objects.values('stop_id').distinct().count()
print(f"\n--- Summary ---")
print(f"Total RouteStop entries: {total_rs}")
print(f"Routes that have stops assigned: {total_routes_with_stops}")
print(f"Stops assigned to routes: {total_stops_with_routes}")
print(f"Total active routes: {BusRoute.objects.filter(is_active=True).count()}")
print(f"Total active stops: {BusStop.objects.filter(is_active=True).count()}")
