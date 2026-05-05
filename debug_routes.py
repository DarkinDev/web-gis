import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bus_management.settings')
django.setup()

from bus.models import BusRoute

print("--- ROUTE DATA DUMP ---")
for r in BusRoute.all_objects.all().order_by('route_number')[:5]:
    print(f"ID: {r.id}, Num: {r.route_number}, Name: {r.name}, Active: {r.is_active}, Deleted: {r.is_deleted}, Color: '{r.color}'")
