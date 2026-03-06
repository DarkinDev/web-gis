"""
Django App Config with PostGIS workaround
"""
from django.apps import AppConfig


class BusManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bus_management'
    
    def ready(self):
        """Patch PostGIS backend after Django is fully loaded"""
        # TEMPORARY WORKAROUND: Patch PostGIS backend to skip extension check
        # This allows migrations to run even if PostGIS is not installed
        # TODO: Install PostGIS and remove this workaround
        try:
            from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as PostGISWrapper
            from django.db.backends.postgresql.base import DatabaseWrapper as PGWrapper
            
            original_prepare = PostGISWrapper.prepare_database
            
            def patched_prepare_database(self):
                """Patched version that skips PostGIS extension if not available"""
                # Call parent PostgreSQL prepare_database
                PGWrapper.prepare_database(self)
                
                # Try to create PostGIS extension, but don't fail if it doesn't exist
                try:
                    with self.cursor() as cursor:
                        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = %s", ["postgis"])
                        if bool(cursor.fetchone()):
                            return
                        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                except Exception as e:
                    # PostGIS not installed - skip silently
                    import warnings
                    warnings.warn(
                        f"PostGIS extension not available: {e}. "
                        "GIS features will not work. Please install PostGIS.",
                        UserWarning
                    )
            
            PostGISWrapper.prepare_database = patched_prepare_database
        except Exception:
            # If patching fails, continue anyway
            pass
