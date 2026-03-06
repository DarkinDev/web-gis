"""
Script tự động tạo database bus_gis với PostGIS extension
Chạy: python create_db.py
"""
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Fix encoding cho Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Thông tin kết nối PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'nguyenducquan123',  # Mật khẩu từ settings.py
}

def create_database():
    """Create database bus_gis and enable PostGIS extension"""
    try:
        # Connect to PostgreSQL (default database)
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'bus_gis'")
        exists = cursor.fetchone()
        
        if exists:
            print("WARNING: Database 'bus_gis' already exists!")
            choice = input("Do you want to drop and recreate it? (y/n): ")
            if choice.lower() == 'y':
                cursor.execute("DROP DATABASE bus_gis;")
                print("OK: Dropped old database")
            else:
                print("Cancelled. Database already exists.")
                cursor.close()
                conn.close()
                return
        
        # Create database
        print("Creating database 'bus_gis'...")
        cursor.execute("CREATE DATABASE bus_gis;")
        print("OK: Created database 'bus_gis'")
        
        cursor.close()
        conn.close()
        
        # Connect to new database to create PostGIS extension
        print("Connecting to database 'bus_gis'...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='bus_gis'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create PostGIS extension
        print("Enabling PostGIS extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        print("OK: PostGIS extension enabled")
        
        # Check PostGIS version
        cursor.execute("SELECT PostGIS_version();")
        version = cursor.fetchone()[0]
        print(f"OK: PostGIS version: {version}")
        
        cursor.close()
        conn.close()
        
        print("\nSUCCESS! Database 'bus_gis' is ready.")
        print("Now you can run: python manage.py migrate")
        
    except psycopg2.OperationalError as e:
        print(f"ERROR: Connection failed: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Password in script matches your PostgreSQL password")
        print("3. User 'postgres' has permission to create databases")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    create_database()
