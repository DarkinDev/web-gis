"""
Custom PostGIS Database Backend - Workaround for missing PostGIS extension
This temporarily bypasses PostGIS extension creation to allow migrations
"""
from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as PostGISDatabaseWrapper


class DatabaseWrapper(PostGISDatabaseWrapper):
    """
    Custom PostGIS wrapper that skips PostGIS extension creation
    if PostGIS is not installed. Use this ONLY as a temporary workaround.
    """
    
    def prepare_database(self):
        """Override to skip PostGIS extension creation if not available"""
        # Call parent's prepare_database (PostgreSQL setup)
        from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as Parent
        super(PostGISDatabaseWrapper, self).prepare_database()
        
        # Try to create PostGIS extension, but don't fail if it doesn't exist
        try:
            with self.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_extension WHERE extname = %s", ["postgis"])
                if bool(cursor.fetchone()):
                    return
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        except Exception as e:
            # PostGIS not installed - skip silently for now
            # This allows migrations to run, but GIS features won't work
            import warnings
            warnings.warn(
                f"PostGIS extension not available: {e}. "
                "GIS features will not work. Please install PostGIS.",
                UserWarning
            )
