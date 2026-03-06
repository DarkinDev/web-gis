# Bus Management WebGIS

Hệ thống WebGIS quản lý xe buýt sử dụng Django + PostGIS với đầy đủ chức năng GIS thực tế.

## 📋 Tính năng

### Chức năng bản đồ
- ✅ Hiển thị bản đồ các tuyến xe buýt
- ✅ Hiển thị các trạm dừng xe buýt
- ✅ Click trạm để xem thông tin (tên trạm, tuyến đi qua)
- ✅ Tìm trạm gần vị trí người dùng nhất (GIS distance)
- ✅ Tìm đường đi giữa 2 trạm
- ✅ Lọc tuyến xe theo số hiệu
- ✅ Hiển thị bán kính phục vụ quanh trạm (buffer GIS)

### Chức năng GIS (PostGIS)
- ✅ Tính khoảng cách giữa 2 điểm (ST_Distance)
- ✅ Tìm trạm gần nhất (nearest neighbor query)
- ✅ Tạo vùng đệm quanh trạm (ST_Buffer)
- ✅ Kiểm tra điểm có nằm trong vùng phục vụ (ST_Contains)

### Quản trị
- ✅ Django Admin với map widget để thêm/sửa/xóa dữ liệu
- ✅ REST API cho frontend

## 🛠 Yêu cầu hệ thống

- Python 3.10+
- PostgreSQL 14+ với PostGIS extension
- GDAL (Geospatial Data Abstraction Library)

## 🚀 Hướng dẫn cài đặt

### 1. Cài đặt PostgreSQL và PostGIS

**Windows:**
- Tải PostgreSQL từ https://www.postgresql.org/download/windows/
- Khi cài đặt, chọn thêm Stack Builder và cài PostGIS

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

### 2. Tạo database

```sql
-- Kết nối PostgreSQL
psql -U postgres

-- Tạo database
CREATE DATABASE bus_gis;

-- Kết nối vào database
\c bus_gis

-- Bật extension PostGIS
CREATE EXTENSION postgis;
```

### 3. Cài đặt GDAL (Windows)

Tải và cài đặt OSGeo4W từ: https://trac.osgeo.org/osgeo4w/

Sau đó thêm vào biến môi trường PATH:
```
C:\OSGeo4W64\bin
```

### 4. Cài đặt project

```bash
# Clone hoặc tải project về
cd d:\gis-web

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 5. Cấu hình database

Mở file `bus_management/settings.py` và chỉnh sửa thông tin kết nối database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bus_gis',
        'USER': 'postgres',
        'PASSWORD': 'your_password',  # Thay đổi password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Chạy migrations và load dữ liệu mẫu

```bash
# Tạo migrations
python manage.py makemigrations bus

# Chạy migrations
python manage.py migrate

# Load dữ liệu mẫu
python manage.py loaddata fixtures/sample_data.json

# Tạo superuser để truy cập admin
python manage.py createsuperuser
```

### 7. Chạy server

```bash
python manage.py runserver
```

Truy cập:
- 🌐 Trang chính: http://localhost:8000
- ⚙️ Admin: http://localhost:8000/admin
- 📡 API: http://localhost:8000/api/

## 📁 Cấu trúc project

```
d:\gis-web\
├── bus_management/          # Django project settings
│   ├── settings.py          # Cấu hình project
│   ├── urls.py               # URL routing chính
│   └── wsgi.py
├── bus/                      # App quản lý xe buýt
│   ├── models.py             # Models: BusRoute, BusStop, RouteStop
│   ├── admin.py              # Django Admin với map widget
│   ├── serializers.py        # REST API serializers
│   ├── views.py              # API views
│   └── urls.py               # API routes
├── gis_tools/                # App công cụ GIS
│   ├── utils.py              # Hàm GIS: distance, buffer, nearest...
│   ├── views.py              # API endpoints cho GIS
│   └── urls.py
├── frontend/                 # App giao diện người dùng
│   ├── views.py              # Views cho template
│   └── urls.py
├── templates/                # HTML templates
│   ├── base.html             # Template chính
│   └── frontend/
│       ├── home.html         # Trang chủ với bản đồ
│       ├── routes.html       # Danh sách tuyến
│       ├── route_detail.html # Chi tiết tuyến
│       └── stops.html        # Danh sách trạm
├── static/
│   ├── css/main.css          # Stylesheet chính
│   └── js/map.js             # JavaScript bản đồ
├── fixtures/
│   └── sample_data.json      # Dữ liệu mẫu
├── manage.py
└── requirements.txt
```

## 🔌 API Endpoints

### Bus Routes
- `GET /api/routes/` - Danh sách tuyến xe
- `GET /api/routes/{id}/` - Chi tiết tuyến
- `GET /api/routes/geojson/` - GeoJSON tất cả tuyến

### Bus Stops
- `GET /api/stops/` - Danh sách trạm dừng
- `GET /api/stops/{id}/` - Chi tiết trạm
- `GET /api/stops/geojson/` - GeoJSON tất cả trạm
- `GET /api/stops/search/?q=keyword` - Tìm kiếm trạm
- `GET /api/stops/nearest/?lat=...&lng=...` - Tìm trạm gần nhất

### GIS Tools
- `GET /api/gis/distance/?lng1=...&lat1=...&lng2=...&lat2=...` - Tính khoảng cách
- `GET /api/gis/nearest/?lat=...&lng=...&limit=5` - Tìm trạm gần nhất
- `GET /api/gis/buffer/?lng=...&lat=...&radius=500` - Tạo vùng đệm
- `GET /api/gis/stops-in-radius/?lng=...&lat=...&radius=500` - Trạm trong bán kính
- `GET /api/gis/find-route/?start_stop_id=...&end_stop_id=...` - Tìm đường

## 🎨 Giao diện

- **Bản đồ fullscreen** với LeafletJS + OpenStreetMap
- **Theme xanh dương - trắng** hiện đại
- **Responsive** cho laptop và điện thoại
- **Popup thông tin đẹp** khi click marker
- **Card UI** với shadow và bo góc

## 📝 License

MIT License - Tự do sử dụng cho mục đích học tập và thương mại.
