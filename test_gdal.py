import os
import sys

# Emulate settings.py logic
OSGEO4W_ROOT = r'C:\Users\Admin\AppData\Local\Programs\OSGeo4W'
os.environ['OSGEO4W_ROOT'] = OSGEO4W_ROOT
os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, 'apps', 'gdal', 'share', 'gdal')
os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + ';' + os.environ['PATH']

try:
    from django.contrib.gis.gdal import HAS_GDAL
    print(f"HAS_GDAL: {HAS_GDAL}")
    from django.contrib.gis.gdal import libgdal
    print(f"GDAL Library: {libgdal.lgdal}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
