"""
Django settings for bus_management project.
WebGIS Bus Management System with PostGIS
"""

from pathlib import Path
import os

# GDAL Configuration for Windows
# Uncomment and adjust path if GDAL is installed via OSGeo4W
if os.name == 'nt':  # Windows
    # Custom OSGeo4W install path found in user's AppData
    OSGEO4W_ROOT = r'C:\Users\Admin\AppData\Local\Programs\OSGeo4W'
    if os.path.exists(OSGEO4W_ROOT):
        os.environ['OSGEO4W_ROOT'] = OSGEO4W_ROOT
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, 'apps', 'gdal', 'share', 'gdal')
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
        os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + ';' + os.environ['PATH']
        GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, 'bin', 'gdal312.dll')
    
    # Try OSGeo4W64 path
    else:
        # Fallback to standard locations just in case
        OSGEO4W = r'C:\OSGeo4W'
        OSGEO4W64 = r'C:\OSGeo4W64'
        if os.path.exists(OSGEO4W):
           OSGEO4W_ROOT = OSGEO4W
        elif os.path.exists(OSGEO4W64):
           OSGEO4W_ROOT = OSGEO4W64
        
        if 'OSGEO4W_ROOT' in locals():
            os.environ['OSGEO4W_ROOT'] = OSGEO4W_ROOT
            os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, 'share', 'gdal')
            os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
            os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + ';' + os.environ['PATH']

    # Try PostgreSQL bundled PostGIS path
    POSTGIS_PATH = r'C:\Program Files\PostgreSQL\18\bin'
    if os.path.exists(POSTGIS_PATH):
        os.environ['PATH'] = POSTGIS_PATH + ';' + os.environ['PATH']

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

# ─── Email Configuration (Mailtrap SMTP) ──────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'YOUR_MAILTRAP_USERNAME'   # ← Thay bằng Username từ Mailtrap
EMAIL_HOST_PASSWORD = 'YOUR_MAILTRAP_PASSWORD'  # ← Thay bằng Password từ Mailtrap
DEFAULT_FROM_EMAIL = 'BusGIS System <noreply@busgis.vn>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Danh sách email quản trị nhận thông báo hệ thống
ADMIN_NOTIFICATION_EMAILS = [
    'your-admin@email.com',  # ← Thay bằng email của bạn
]

# ─── Auth Settings ─────────────────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
PASSWORD_RESET_TIMEOUT = 86400  # Link reset hết hạn sau 24h
