import json
import requests
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from bus.models import BusStop

class Command(BaseCommand):
    help = 'Import bus stops from OpenStreetMap for Ho Chi Minh City'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching data from Overpass API...')
        
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = """
        [out:json];
        area["name"="Thành phố Hồ Chí Minh"]->.searchArea;
        (
          node["highway"="bus_stop"](area.searchArea);
        );
        out body;
        """
        
        try:
            response = requests.get(overpass_url, params={'data': overpass_query})
            response.raise_for_status()
            data = response.json()
            
            elements = data.get('elements', [])
            total_elements = len(elements)
            self.stdout.write(f'Found {total_elements} bus stops.')
            
            created_count = 0
            updated_count = 0
            
            for element in elements:
                lat = element.get('lat')
                lon = element.get('lon')
                tags = element.get('tags', {})
                
                if not lat or not lon:
                    continue
                    
                # Prepare data
                name = tags.get('name', tags.get('name:vi', 'Trạm xe buýt'))
                code = tags.get('ref', tags.get('bus_stop:ref'))
                has_shelter = tags.get('shelter') == 'yes'
                has_bench = tags.get('bench') == 'yes'
                
                # Create geometry
                location = Point(lon, lat, srid=4326)
                
                # Check for existing stop nearby (within 10m) to avoid duplicates if running multiple times
                # or if OSM data is messy. 
                # Ideally we use a unique ID, but 'ref' isn't always present/unique in OSM.
                # 'id' from OSM is unique but we don't strictly store it in our model yet (could leverage if needed).
                
                # Simple strategy: If code exists, match by code. Else match by location buffer.
                stop = None
                
                if code:
                    stop = BusStop.objects.filter(code=code).first()
                
                if not stop:
                    # Check spatial proximity (within 10 meters)
                    start_point = location
                    # simple dwithin check
                    stop = BusStop.objects.filter(location__dwithin=(location, 0.0001)).first() # approx 10m
                
                defaults = {
                    'name': name,
                    'address': tags.get('website', ''), # Using website field or similar for address if available, usually address is separate
                    'has_shelter': has_shelter,
                    'has_bench': has_bench,
                    'is_active': True
                }
                
                if stop:
                    # Update
                    for key, value in defaults.items():
                        setattr(stop, key, value)
                    stop.location = location # Update location just in case
                    stop.save()
                    updated_count += 1
                else:
                    # Create
                    BusStop.objects.create(
                        name=name,
                        code=code,
                        location=location,
                        has_shelter=has_shelter,
                        has_bench=has_bench,
                        is_active=True
                    )
                    created_count += 1
                    
                if (created_count + updated_count) % 100 == 0:
                     self.stdout.write(f'Processed {created_count + updated_count} stops...')

            self.stdout.write(self.style.SUCCESS(f'Successfully imported bus stops. Created: {created_count}, Updated: {updated_count}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
