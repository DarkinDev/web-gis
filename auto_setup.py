"""
BusGIS WebGIS - Auto Setup Script
Tu dong phat hien, cau hinh va cai dat he thong.
"""
import os, sys, subprocess, glob, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, 'bus_management', 'settings.py')

def ok(msg):  print(f"  [OK] {msg}")
def warn(msg): print(f"  [!!] {msg}")
def err(msg):  print(f"  [XX] {msg}")

# ── Auto-detect OSGeo4W ─────────────────────────────────────────────
def find_osgeo4w():
    candidates = [
        r'C:\OSGeo4W',
        r'C:\OSGeo4W64',
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'OSGeo4W'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'OSGeo4W'),
    ]
    for user_dir in glob.glob(r'C:\Users\*'):
        candidates.append(os.path.join(user_dir, 'AppData', 'Local', 'Programs', 'OSGeo4W'))
    for p in candidates:
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, 'bin')):
            return p
    return None

def find_gdal_dll(root):
    for dll in sorted(glob.glob(os.path.join(root, 'bin', 'gdal*.dll')), reverse=True):
        if re.match(r'gdal\d+\.dll$', os.path.basename(dll)):
            return os.path.basename(dll)
    return None

# ── Auto-detect PostgreSQL ──────────────────────────────────────────
def find_postgresql():
    base = r'C:\Program Files\PostgreSQL'
    if not os.path.isdir(base):
        return None, None
    for v in sorted(os.listdir(base), key=lambda x: int(x) if x.isdigit() else 0, reverse=True):
        if os.path.exists(os.path.join(base, v, 'bin', 'psql.exe')):
            return os.path.join(base, v, 'bin'), v
    return None, None

def test_pg(psql_dir, pwd):
    env = os.environ.copy()
    env['PGPASSWORD'] = pwd
    try:
        r = subprocess.run([os.path.join(psql_dir, 'psql.exe'), '-U', 'postgres', '-c', 'SELECT 1;'],
                           capture_output=True, text=True, env=env, timeout=10)
        return r.returncode == 0
    except:
        return False

# ── Update settings.py ──────────────────────────────────────────────
def update_settings(osgeo, gdal_dll, pw, pg_ver):
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r"OSGEO4W_ROOT = r'[^']*'", f"OSGEO4W_ROOT = r'{osgeo}'", c, count=1)
    if gdal_dll:
        c = re.sub(r"'gdal\d+\.dll'", f"'{gdal_dll}'", c)
    c = re.sub(r"'PASSWORD': '[^']*'", f"'PASSWORD': '{pw}'", c)
    c = re.sub(r"POSTGIS_PATH = r'[^']*'", f"POSTGIS_PATH = r'C:\\Program Files\\PostgreSQL\\{pg_ver}\\bin'", c)
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.write(c)

# ── Create database ─────────────────────────────────────────────────
def create_db(psql_dir, pwd):
    env = os.environ.copy()
    env['PGPASSWORD'] = pwd
    psql = os.path.join(psql_dir, 'psql.exe')
    
    r = subprocess.run([psql, '-U', 'postgres', '-tAc',
                        "SELECT 1 FROM pg_database WHERE datname='bus_gis';"],
                       capture_output=True, text=True, env=env)
    if '1' not in r.stdout:
        subprocess.run([psql, '-U', 'postgres', '-c', 'CREATE DATABASE bus_gis;'], env=env)
        ok("Database 'bus_gis' da tao")
    else:
        ok("Database 'bus_gis' da ton tai")
    
    r = subprocess.run([psql, '-U', 'postgres', '-d', 'bus_gis',
                        '-c', 'CREATE EXTENSION IF NOT EXISTS postgis;'],
                       capture_output=True, text=True, env=env)
    if r.returncode == 0:
        ok("PostGIS extension OK")
        return True
    else:
        err(f"PostGIS loi: {r.stderr}")
        return False

# ── Main ────────────────────────────────────────────────────────────
def main():
    print()
    print("=" * 56)
    print("      BusGIS WebGIS - Auto Setup")
    print("=" * 56)
    
    # 1. OSGeo4W
    print("\n--- [1/5] Phat hien OSGeo4W (GDAL) ---")
    osgeo = find_osgeo4w()
    if osgeo:
        ok(f"OSGeo4W: {osgeo}")
        gdal_dll = find_gdal_dll(osgeo)
        if gdal_dll:
            ok(f"GDAL DLL: {gdal_dll}")
        else:
            warn("Khong tim thay GDAL DLL, se giu nguyen cau hinh.")
            gdal_dll = None
    else:
        err("Khong tim thay OSGeo4W!")
        print("  Cai tu: https://trac.osgeo.org/osgeo4w/")
        osgeo = input("  Nhap duong dan OSGeo4W (hoac Enter de bo qua): ").strip()
        if not osgeo or not os.path.isdir(osgeo):
            warn("Bo qua cau hinh OSGeo4W. Ban can cau hinh thu cong trong settings.py")
            osgeo = None
            gdal_dll = None
        else:
            gdal_dll = find_gdal_dll(osgeo)
    
    # 2. PostgreSQL
    print("\n--- [2/5] Phat hien PostgreSQL ---")
    pg_path, pg_ver = find_postgresql()
    if pg_path:
        ok(f"PostgreSQL {pg_ver}: {pg_path}")
    else:
        err("Khong tim thay PostgreSQL! Cai tu:")
        print("  https://www.enterprisedb.com/downloads/postgres-postgresql-downloads")
        input("  Nhan Enter de thoat...")
        sys.exit(1)
    
    # 3. Password & connection test
    print("\n--- [3/5] Ket noi PostgreSQL ---")
    pw = input("  Nhap mat khau PostgreSQL (user: postgres): ").strip()
    if not test_pg(pg_path, pw):
        err("Khong the ket noi! Kiem tra mat khau va PostgreSQL service.")
        input("  Nhan Enter de thoat...")
        sys.exit(1)
    ok("Ket noi thanh cong!")
    
    # 4. Configure settings.py
    print("\n--- [4/5] Cau hinh settings.py ---")
    if osgeo:
        update_settings(osgeo, gdal_dll, pw, pg_ver)
        ok("settings.py da cap nhat")
    else:
        # Only update password and pg version
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            c = f.read()
        c = re.sub(r"'PASSWORD': '[^']*'", f"'PASSWORD': '{pw}'", c)
        c = re.sub(r"POSTGIS_PATH = r'[^']*'",
                   f"POSTGIS_PATH = r'C:\\Program Files\\PostgreSQL\\{pg_ver}\\bin'", c)
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            f.write(c)
        ok("settings.py da cap nhat (password + PostgreSQL path)")
    
    # 5. Database + migrations + data
    print("\n--- [5/5] Tao database, migrations, du lieu ---")
    if not create_db(pg_path, pw):
        err("Loi PostGIS. Dam bao da cai PostGIS qua Stack Builder.")
        input("  Nhan Enter de thoat...")
        sys.exit(1)
    
    print("\n  Chay migrations...")
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'], cwd=BASE_DIR)
    subprocess.run([sys.executable, 'manage.py', 'migrate'], cwd=BASE_DIR)
    ok("Migrations xong")
    
    fixture = os.path.join(BASE_DIR, 'fixtures', 'sample_data.json')
    if os.path.exists(fixture):
        subprocess.run([sys.executable, 'manage.py', 'loaddata', fixture], cwd=BASE_DIR)
        ok("Du lieu mau da nap")
    
    # Create admin
    env = os.environ.copy()
    env['DJANGO_SUPERUSER_USERNAME'] = 'admin'
    env['DJANGO_SUPERUSER_EMAIL'] = 'admin@busgis.vn'
    env['DJANGO_SUPERUSER_PASSWORD'] = 'admin123'
    r = subprocess.run([sys.executable, 'manage.py', 'createsuperuser', '--noinput'],
                       capture_output=True, text=True, env=env, cwd=BASE_DIR)
    if r.returncode == 0:
        ok("Tai khoan admin da tao (admin / admin123)")
    else:
        ok("Tai khoan admin da ton tai hoac da tao")
    
    # Create sample users
    script = os.path.join(BASE_DIR, 'create_users.py')
    if os.path.exists(script):
        subprocess.run([sys.executable, script], capture_output=True, cwd=BASE_DIR)
        ok("User mau da tao (staff/staff123, khach/user123)")
    
    # Done
    print()
    print("=" * 56)
    print("  HOAN TAT! Chay lenh sau de khoi dong server:")
    print()
    print("    python manage.py runserver")
    print()
    print("  Truy cap: http://127.0.0.1:8000")
    print()
    print("  Tai khoan:")
    print("    Admin : admin / admin123")
    print("    Staff : staff / staff123")
    print("    User  : khach / user123")
    print("=" * 56)
    print()

if __name__ == '__main__':
    main()
