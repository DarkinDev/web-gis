"""
Django settings for bus_management project.
WebGIS Bus Management System with PostGIS
"""

from pathlib import Path
import os
import sys
from ctypes import CDLL, WINFUNCTYPE

# GDAL Configuration for Windows - MUST BE FIRST!
if os.name == 'nt':  # Windows
    # Try standard OSGeo4W locations
    OSGEO4W64 = r'C:\OSGeo4W64'
    OSGEO4W = r'C:\OSGeo4W'
    
    # Priority: standard locations
    if os.path.exists(OSGEO4W):
        OSGEO4W_ROOT = OSGEO4W
    elif os.path.exists(OSGEO4W64):
        OSGEO4W_ROOT = OSGEO4W64
    else:
        OSGEO4W_ROOT = None
    
    if OSGEO4W_ROOT:
        # Set environment variables for GDAL
        os.environ['OSGEO4W_ROOT'] = OSGEO4W_ROOT
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, 'share', 'gdal')
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
        os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + ';' + os.environ['PATH']
        
        # Directly load GDAL DLL with full path
        gdal_dll = os.path.join(OSGEO4W_ROOT, 'bin', 'gdal312.dll')
        if os.path.exists(gdal_dll):
            try:
                # Load with full path
                gdal_lib = CDLL(gdal_dll)
                # Register in sys.modules so Django can find it
                os.environ['GDAL_LIBRARY_PATH'] = gdal_dll
                
                # Monkey-patch ctypes.util.find_library to return our DLL path
                import ctypes.util
                original_find_library = ctypes.util.find_library
                def patched_find_library(name):
                    if 'gdal' in name.lower():
                        return gdal_dll
                    return original_find_library(name)
                ctypes.util.find_library = patched_find_library
            except Exception as e:
                print(f"Warning: Error configuring GDAL: {e}")
        else:
            # Fallback: try to find any gdal DLL
            import glob
            gdal_dlls = glob.glob(os.path.join(OSGEO4W_ROOT, 'bin', 'gdal*.dll'))
            if gdal_dlls:
                try:
                    gdal_dll = gdal_dlls[0]
                    gdal_lib = CDLL(gdal_dll)
                    os.environ['GDAL_LIBRARY_PATH'] = gdal_dll
                    
                    # Monkey-patch ctypes.util.find_library
                    import ctypes.util
                    original_find_library = ctypes.util.find_library
                    def patched_find_library(name):
                        if 'gdal' in name.lower():
                            return gdal_dll
                        return original_find_library(name)
                    ctypes.util.find_library = patched_find_library
                except Exception as e:
                    print(f"Warning: Error configuring GDAL: {e}")

    # Try PostgreSQL bundled PostGIS path
    for pg_version in ['18', '17', '16', '15', '14']:
        POSTGIS_PATH = rf'C:\Program Files\PostgreSQL\{pg_version}\bin'
        if os.path.exists(POSTGIS_PATH):
            os.environ['PATH'] = POSTGIS_PATH + ';' + os.environ['PATH']
            break

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bus-management-webgis-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    
    # Third party apps
    'leaflet',
    'rest_framework',
    'rest_framework_gis',
    'corsheaders',
    
    # Local apps
    'bus',
    'gis_tools',
    'frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bus_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bus_management.wsgi.application'

# Database - PostgreSQL with PostGIS
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bus_gis',
        'USER': 'postgres',
        'PASSWORD': 'nguyenducquan123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Leaflet configuration
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (10.8231, 106.6297),  # Ho Chi Minh City
    'DEFAULT_ZOOM': 13,
    'MIN_ZOOM': 10,
    'MAX_ZOOM': 19,
    'TILES': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'ATTRIBUTION_PREFIX': 'Bus Management WebGIS',
    'PLUGINS': {
        'forms': {
            'auto-include': True
        }
    }
}

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
