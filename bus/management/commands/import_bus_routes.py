import json
import requests
import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, LineString
from bus.models import BusRoute, BusStop, RouteStop

class Command(BaseCommand):
    help = 'Import bus routes from OpenStreetMap for Ho Chi Minh City'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching route data from Overpass API...')
        
        overpass_url = "http://overpass-api.de/api/interpreter"
        # Query to get bus routes in HCMC
        # We ask for relations with route=bus
        # We also ask for 'out geom' to get the geometry of the relation (the path) and members
        overpass_query = """
        [out:json][timeout:60];
        area["name"="Thành phố Hồ Chí Minh"]->.searchArea;
        (
          relation["type"="route"]["route"="bus"](area.searchArea);
        );
        out body geom;
        """
        
        try:
            response = requests.get(overpass_url, params={'data': overpass_query})
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Overpass API Error: {response.text}'))
            response.raise_for_status()
            data = response.json()
            
            elements = data.get('elements', [])
            total_elements = len(elements)
            self.stdout.write(f'Found {total_elements} routes.')
            
            created_count = 0
            updated_count = 0
            
            # Pre-fetch all stops to memory to speed up lookup (optional but good for performance)
            # However, spatial lookup is better done in DB if we rely on dwithin
            
            for element in elements:
                tags = element.get('tags', {})
                members = element.get('members', [])
                
                route_ref = tags.get('ref') or tags.get('name', 'Unknown')
                if not route_ref:
                    continue
                    
                route_name = tags.get('name', f"Tuyến {route_ref}")
                route_color = tags.get('colour', '#%06x' % random.randint(0, 0xFFFFFF))
                if not route_color.startswith('#'):
                    # Handle non-hex colors (basic ones)
                    colors = {
                        'red': '#FF0000', 'green': '#008000', 'blue': '#0000FF', 
                        'yellow': '#FFFF00', 'orange': '#FFA500', 'purple': '#800080'
                    }
                    route_color = colors.get(route_color.lower(), '#3388ff')

                # Create or get Route
                route, created = BusRoute.objects.update_or_create(
                    route_number=route_ref,
                    defaults={
                        'name': route_name[:200], # Trucate if too long
                        'description': tags.get('description', '') or tags.get('from', '') + ' - ' + tags.get('to', ''),
                        'start_point': tags.get('from', 'Unknown')[:200],
                        'end_point': tags.get('to', 'Unknown')[:200],
                        'color': route_color[:7],
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                
                # Process members to find stops and build geometry
                # Valid roles for stops: stop, platform, stop_entry_only, stop_exit_only
                stop_order = 0
                points = []
                
                # Clear existing stops for this route to avoid duplicates on re-run
                RouteStop.objects.filter(route=route).delete()
                
                for member in members:
                    m_type = member.get('type')
                    m_role = member.get('role')
                    m_lat = member.get('lat')
                    m_lon = member.get('lon')
                    m_geom = member.get('geometry') # For ways
                    
                    # 1. Build Route Geometry
                    # If relation has geometry (it should with 'out geom'), we can use it
                    # But often relations are mixed. 'out geom' gives geometry for ways.
                    # Simple approach: Connect the stop points.
                    # Better approach: Use the way members to build the path.
                    
                    if m_type == 'node' and (m_role in ['stop', 'platform', 'stop_entry_only', 'stop_exit_only'] or m_role == ''):
                        if m_lat and m_lon:
                            pt = Point(m_lon, m_lat, srid=4326)
                            points.append(pt)
                            
                            # Find matching BusStop in DB
                            # We use a small buffer (e.g., 20m) to find the stop we imported earlier
                            # Prioritize exact match if we had codes, but we rely on location now.
                            stop = BusStop.objects.filter(location__dwithin=(pt, 0.0002)).first() # ~20m
                            
                            if stop:
                                try:
                                    RouteStop.objects.create(
                                        route=route,
                                        stop=stop,
                                        order=stop_order,
                                        distance_from_start=None
                                    )
                                    stop_order += 1
                                except Exception as e:
                                    # Skip if duplicate stop in route (due to unique_together constraint)
                                    # Real fix would be to remove the constraint, but for now we skip.
                                    pass
                    
                    # Collect points for geometry (nodes + ways)
                    # For simplicity in this script, we'll build geometry from STOPS + WAY points if available
                    # A robust implementation would stitch ways. Here we might just use the stops as the path skeleton
                    # or if OSM returns full geometry.
                    
                    # With 'out geom', ways have a 'geometry' list of points.
                    if m_type == 'way' and m_geom:
                        for pt_dict in m_geom:
                            points.append(Point(pt_dict['lon'], pt_dict['lat'], srid=4326))

                # Create LineString for route
                if len(points) > 1:
                    try:
                        route.geometry = LineString(points, srid=4326)
                        route.save()
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not create geometry for route {route_ref}: {e}"))
                
                self.stdout.write(f"Processed route {route_ref}: {stop_order} stops")

            self.stdout.write(self.style.SUCCESS(f'Successfully imported routes. Created: {created_count}, Updated: {updated_count}'))
            
        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
