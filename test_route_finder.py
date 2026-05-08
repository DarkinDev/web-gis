import os, sys, io, django
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bus_management.settings'
django.setup()

from gis_tools.utils import get_route_between_stops

# Test: Ben xe Cu Chi (3467) -> Cho Ben Thanh (401)
print("=== Test: Bến xe Củ Chi -> Chợ Bến Thành ===")
results, subs = get_route_between_stops(3467, 401)
print(f"Routes found: {len(results)}")
if subs:
    print("Substitutions:")
    for k, v in subs.items():
        print(f"  {k}: {v['original_stop_name']} -> {v['name']} ({v['distance_m']}m)")
if results:
    r = results[0]
    print(f"First result type: {r['type']}")
    if r['type'] == 'direct':
        print(f"  Route: {r['route_number']} - {r['route_name']}")
    elif r['type'] == 'transfer':
        print(f"  Segment 1: {r['segments'][0]['route_number']}")
        print(f"  Transfer at: {r['transfer_stop']['name']}")
        print(f"  Segment 2: {r['segments'][1]['route_number']}")
