"""Quick script to check if PostGIS is installed"""
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        user='postgres',
        password='nguyenducquan123',
        database='bus_gis'
    )
    cur = conn.cursor()
    
    # Check PostGIS extension
    cur.execute("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
    result = cur.fetchone()
    
    if result:
        print("OK: PostGIS is installed!")
        # Get version
        cur.execute("SELECT PostGIS_version();")
        version = cur.fetchone()[0]
        print(f"   Version: {version}")
    else:
        print("ERROR: PostGIS is NOT installed")
        print("\nTo install PostGIS:")
        print("1. Use Stack Builder (PostgreSQL 13)")
        print("2. Or download from: https://postgis.net/windows_downloads/")
        print("3. Then run: python create_db.py")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
