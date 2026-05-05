import urllib.request
import json

r = urllib.request.urlopen('http://127.0.0.1:8000/api/routes/geojson-from-stops/')
d = json.loads(r.read())
print('OK! Features:', len(d.get('features', [])))
for f in d['features']:
    props = f['properties']
    coords = f['geometry']['coordinates']
    print(f"  {props['route_number']}: {props['name']} - {len(coords)} points")
