# 🚍 Hướng Dẫn Cài Đặt BusGIS WebGIS - Từ A đến Z

> Hướng dẫn cài đặt **đầy đủ** trên một máy Windows **hoàn toàn mới**, đảm bảo chạy trơn tru.

---

## 📋 Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cài đặt Python](#2-cài-đặt-python)
3. [Cài đặt PostgreSQL + PostGIS](#3-cài-đặt-postgresql--postgis)
4. [Cài đặt OSGeo4W (GDAL)](#4-cài-đặt-osgeo4w-gdal)
5. [Clone project](#5-clone-project)
6. [Tạo Virtual Environment & cài packages](#6-tạo-virtual-environment--cài-packages)
7. [Cấu hình Database](#7-cấu-hình-database)
8. [Cấu hình settings.py](#8-cấu-hình-settingspy)
9. [Chạy Migrations & nạp dữ liệu mẫu](#9-chạy-migrations--nạp-dữ-liệu-mẫu)
10. [Tạo tài khoản Admin & User mẫu](#10-tạo-tài-khoản-admin--user-mẫu)
11. [Chạy server](#11-chạy-server)
12. [Khắc phục lỗi thường gặp](#12-khắc-phục-lỗi-thường-gặp)

---

## 1. Yêu cầu hệ thống

| Thành phần       | Phiên bản khuyến nghị      |
|------------------|---------------------------|
| **HĐH**         | Windows 10/11 (64-bit)    |
| **Python**       | 3.12 hoặc 3.13 hoặc 3.14 |
| **PostgreSQL**   | 16 hoặc 17 hoặc 18       |
| **PostGIS**      | 3.4+ (đi kèm PostgreSQL) |
| **OSGeo4W**      | Bản mới nhất              |
| **Git**          | Bản mới nhất              |
| **RAM**          | Tối thiểu 4GB             |
| **Dung lượng**   | ~2GB trống                |

---

## 2. Cài đặt Python

### 2.1. Tải Python
- Vào https://www.python.org/downloads/
- Tải **Python 3.12.x** hoặc mới hơn (bản **Windows installer 64-bit**)

### 2.2. Cài đặt
- **BẮT BUỘC**: Tick ✅ **"Add python.exe to PATH"** ở màn hình đầu tiên
- Chọn **"Install Now"** hoặc **"Customize installation"** → tick hết các option
- Chờ cài xong

### 2.3. Kiểm tra
Mở **Command Prompt** (hoặc PowerShell):
```cmd
python --version
pip --version
```
Kết quả mong đợi:
```
Python 3.12.x
pip 24.x.x
```

---

## 3. Cài đặt PostgreSQL + PostGIS

### 3.1. Tải PostgreSQL
- Vào https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
- Tải **PostgreSQL 16** hoặc **17** hoặc **18** cho Windows x86-64

### 3.2. Cài đặt PostgreSQL
1. Chạy file `.exe` vừa tải
2. **Chọn đường dẫn cài**: giữ mặc định `C:\Program Files\PostgreSQL\18`
3. **Chọn components**: tick hết (đặc biệt **Stack Builder**)
4. **Data directory**: giữ mặc định
5. **Đặt mật khẩu cho user `postgres`**: **GHI NHỚ mật khẩu này** (ví dụ: `postgres123`)
6. **Port**: giữ mặc định `5432`
7. **Locale**: `Vietnamese, Vietnam` hoặc `Default locale`
8. Nhấn **Next** → **Install** → chờ cài xong

### 3.3. Cài đặt PostGIS qua Stack Builder
1. Sau khi cài PostgreSQL xong, **Stack Builder** sẽ tự mở (hoặc tìm trong Start Menu: **Stack Builder**)
2. Chọn PostgreSQL version vừa cài → **Next**
3. Mở mục **Spatial Extensions** → tick ✅ **PostGIS 3.4 Bundle** (hoặc mới hơn)
4. Nhấn **Next** → **Download** → **Install**
5. Trong quá trình cài PostGIS:
   - Tick ✅ **Create spatial database** (không bắt buộc)
   - Giữ mặc định các option khác

### 3.4. Thêm PostgreSQL vào PATH (nếu chưa có)
1. Nhấn `Win + R` → gõ `sysdm.cpl` → Enter
2. Tab **Advanced** → **Environment Variables**
3. Ở **System variables** → tìm `Path` → **Edit**
4. Thêm dòng mới: `C:\Program Files\PostgreSQL\18\bin` (sửa số version cho đúng)
5. **OK** → **OK** → **OK**

### 3.5. Kiểm tra
```cmd
psql --version
```
Kết quả: `psql (PostgreSQL) 18.x`

---

## 4. Cài đặt OSGeo4W (GDAL)

> ⚠️ **QUAN TRỌNG**: Django GIS cần thư viện GDAL để xử lý dữ liệu không gian.

### 4.1. Tải OSGeo4W
- Vào https://trac.osgeo.org/osgeo4w/
- Nhấn **OSGeo4W network installer** (64-bit) → tải file `osgeo4w-setup.exe`

### 4.2. Cài đặt
1. Chạy `osgeo4w-setup.exe`
2. Chọn **Advanced Install** → **Next**
3. Chọn **Install from Internet** → **Next**
4. **Root Directory**: 
   - Chọn đường dẫn ví dụ: `C:\OSGeo4W` (đơn giản, ngắn gọn)
   - Hoặc cài vào `C:\Users\<TenUser>\AppData\Local\Programs\OSGeo4W`
5. **Next** qua các bước chọn proxy, mirror
6. Ở màn hình **Select Packages**, tìm và tick cài các gói sau:
   - `gdal` (trong nhóm **Libs**)
   - `proj` (trong nhóm **Libs**)
   - `geos` (trong nhóm **Libs**)
7. Nhấn **Next** → chờ cài xong

### 4.3. Xác định file `gdal*.dll`
Sau khi cài, bạn cần tìm tên chính xác file DLL của GDAL:
```cmd
dir "C:\OSGeo4W\bin\gdal*.dll"
```
Ghi nhớ tên file, ví dụ: `gdal312.dll` hoặc `gdal309.dll`. Sẽ dùng ở bước cấu hình.

---

## 5. Clone project

### 5.1. Cài Git (nếu chưa có)
- Tải từ https://git-scm.com/download/win → cài đặt giữ mặc định

### 5.2. Clone
Mở **Command Prompt** hoặc **PowerShell**, chọn thư mục muốn lưu project:
```cmd
cd D:\
mkdir gis-web
cd gis-web
git clone -b final https://github.com/DarkinDev/web-gis.git
cd web-gis
```

---

## 6. Tạo Virtual Environment & cài packages

### 6.1. Tạo môi trường ảo
```cmd
python -m venv venv
```

### 6.2. Kích hoạt môi trường ảo

**Command Prompt:**
```cmd
venv\Scripts\activate
```

**PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

> ⚠️ Nếu PowerShell báo lỗi "cannot be loaded because running scripts is disabled", chạy lệnh sau **với quyền Admin**:
> ```powershell
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Khi kích hoạt thành công, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.

### 6.3. Cài đặt packages
```cmd
pip install -r requirements.txt
```

Danh sách packages sẽ được cài:
| Package                    | Mô tả                           |
|---------------------------|----------------------------------|
| Django 4.2.x              | Web framework                    |
| psycopg2-binary           | PostgreSQL driver                |
| django-leaflet            | Leaflet maps cho Django          |
| djangorestframework       | REST API                         |
| djangorestframework-gis   | GIS serializers                  |
| django-cors-headers       | CORS support                     |
| requests                  | HTTP client                      |

### 6.4. Cài GDAL Python binding
```cmd
pip install GDAL
```

> ⚠️ Nếu lệnh trên bị lỗi, thử cách sau:
> 1. Vào https://github.com/cgohlke/geospatial-wheels/releases
> 2. Tải file `.whl` phù hợp với phiên bản Python của bạn (ví dụ: `GDAL‑3.9.x‑cp312‑cp312‑win_amd64.whl`)
> 3. Cài bằng pip:
> ```cmd
> pip install đường_dẫn_tới_file.whl
> ```

---

## 7. Cấu hình Database

### 7.1. Mở pgAdmin hoặc dùng psql
**Cách 1: Dùng psql (CMD)**
```cmd
psql -U postgres
```
Nhập mật khẩu đã đặt ở bước 3.2.

**Cách 2: Mở pgAdmin** (có sẵn sau khi cài PostgreSQL) → đăng nhập

### 7.2. Tạo database
Trong psql hoặc pgAdmin Query Tool:
```sql
CREATE DATABASE bus_gis;
```

### 7.3. Bật PostGIS extension
```sql
\c bus_gis
CREATE EXTENSION IF NOT EXISTS postgis;
```

Kiểm tra PostGIS đã bật:
```sql
SELECT PostGIS_Version();
```
Kết quả mong đợi: `3.4 USE_GEOS=1 USE_PROJ=1 ...`

---

## 8. Cấu hình settings.py

Mở file `bus_management/settings.py` và chỉnh sửa các mục sau:

### 8.1. Cấu hình GDAL (dòng 11-40)
Sửa đường dẫn OSGeo4W cho đúng với máy của bạn:

```python
if os.name == 'nt':  # Windows
    # ── Sửa đường dẫn OSGeo4W đúng với máy bạn ──
    OSGEO4W_ROOT = r'C:\OSGeo4W'   # ← Sửa đường dẫn nếu cài ở chỗ khác
    if os.path.exists(OSGEO4W_ROOT):
        os.environ['OSGEO4W_ROOT'] = OSGEO4W_ROOT
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, 'apps', 'gdal', 'share', 'gdal')
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
        os.environ['PATH'] = os.path.join(OSGEO4W_ROOT, 'bin') + ';' + os.environ['PATH']
        GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, 'bin', 'gdal312.dll')  # ← Sửa tên file dll cho đúng
```

> 💡 **Lưu ý**: Tên file `gdal312.dll` có thể khác tùy version GDAL. Dùng lệnh `dir C:\OSGeo4W\bin\gdal*.dll` để xác định.

### 8.2. Cấu hình Database (dòng 107-116)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bus_gis',
        'USER': 'postgres',
        'PASSWORD': 'MẬT_KHẨU_POSTGRESQL_CỦA_BẠN',  # ← Sửa mật khẩu
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 8.3. Cấu hình đường dẫn PostgreSQL (dòng 38-40)
```python
POSTGIS_PATH = r'C:\Program Files\PostgreSQL\18\bin'  # ← Sửa version PostgreSQL cho đúng
```

### 8.4. (Tùy chọn) Cấu hình Email - Mailtrap (dòng 174-187)
Nếu muốn dùng tính năng gửi email thông báo:
1. Tạo tài khoản tại https://mailtrap.io
2. Lấy SMTP credentials
3. Sửa:
```python
EMAIL_HOST_USER = 'username_mailtrap_của_bạn'
EMAIL_HOST_PASSWORD = 'password_mailtrap_của_bạn'
```

> Nếu không cần email, hệ thống vẫn chạy bình thường, chỉ bỏ qua phần thông báo email.

---

## 9. Chạy Migrations & nạp dữ liệu mẫu

> ⚠️ Đảm bảo đã kích hoạt `(venv)` trước khi chạy.

### 9.1. Chạy migrations
```cmd
python manage.py makemigrations
python manage.py migrate
```

Kết quả mong đợi: Nhiều dòng `Applying bus.0001_initial... OK`, `Applying bus.0004_review... OK`, v.v.

### 9.2. Nạp dữ liệu mẫu (5 tuyến xe, 15 trạm, 22 điểm dừng)
```cmd
python manage.py loaddata fixtures/sample_data.json
```

Kết quả: `Installed 42 object(s) from 1 fixture(s)`

---

## 10. Tạo tài khoản Admin & User mẫu

### 10.1. Tạo tài khoản Superuser (Admin)
```cmd
python manage.py createsuperuser
```
Nhập thông tin:
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123` (hoặc mật khẩu mạnh hơn)

### 10.2. Tạo tài khoản Staff và User thường (tùy chọn)
```cmd
python create_users.py
```
Sẽ tạo 2 tài khoản:

| Loại         | Username | Password   | Quyền          |
|-------------|----------|------------|----------------|
| Staff       | `staff`  | `staff123` | Nhân viên      |
| User thường | `khach`  | `user123`  | Người dùng     |

---

## 11. Chạy server

### 11.1. Khởi động Django
```cmd
python manage.py runserver
```

### 11.2. Truy cập web
Mở trình duyệt và vào:

| Trang                   | URL                                      |
|------------------------|------------------------------------------|
| 🏠 **Trang chủ**       | http://127.0.0.1:8000/                   |
| 🗺️ **Bản đồ**         | http://127.0.0.1:8000/home/              |
| 🚌 **Danh sách tuyến** | http://127.0.0.1:8000/routes/            |
| 🚏 **Danh sách trạm**  | http://127.0.0.1:8000/stops/             |
| 🔑 **Đăng nhập**       | http://127.0.0.1:8000/accounts/login/    |
| ⚙️ **Admin**           | http://127.0.0.1:8000/admin/             |
| 📡 **API tuyến**       | http://127.0.0.1:8000/api/routes/        |
| 📡 **API trạm**        | http://127.0.0.1:8000/api/stops/         |

### 11.3. Dừng server
Nhấn `Ctrl + C` trong terminal.

---

## 12. Khắc phục lỗi thường gặp

### ❌ Lỗi: `Could not find the GDAL library` hoặc `OSError: [WinError 126]`
**Nguyên nhân**: Django không tìm thấy GDAL DLL.

**Cách sửa**:
1. Kiểm tra file GDAL DLL tồn tại:
   ```cmd
   dir "C:\OSGeo4W\bin\gdal*.dll"
   ```
2. Sửa tên DLL trong `settings.py` cho khớp:
   ```python
   GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_ROOT, 'bin', 'gdal309.dll')  # sửa tên cho đúng
   ```
3. Đảm bảo `C:\OSGeo4W\bin` có trong PATH

---

### ❌ Lỗi: `django.db.utils.OperationalError: could not connect to server`
**Nguyên nhân**: PostgreSQL chưa chạy hoặc sai mật khẩu.

**Cách sửa**:
1. Kiểm tra PostgreSQL đang chạy:
   - Mở **Services** (`Win + R` → `services.msc`)
   - Tìm `postgresql-x64-18` → đảm bảo Status = **Running**
2. Kiểm tra mật khẩu đúng trong `settings.py`
3. Test kết nối:
   ```cmd
   psql -U postgres -d bus_gis
   ```

---

### ❌ Lỗi: `relation "bus_busroute" does not exist`
**Nguyên nhân**: Chưa chạy migrations.

**Cách sửa**:
```cmd
python manage.py makemigrations bus
python manage.py migrate
```

---

### ❌ Lỗi: `type "geometry" does not exist` hoặc `PostGIS extension not found`
**Nguyên nhân**: Chưa bật PostGIS extension cho database.

**Cách sửa**:
```cmd
psql -U postgres -d bus_gis -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

---

### ❌ Lỗi: `ModuleNotFoundError: No module named 'django'`
**Nguyên nhân**: Chưa kích hoạt virtual environment.

**Cách sửa**:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

---

### ❌ Lỗi: `running scripts is disabled on this system` (PowerShell)
**Cách sửa** (chạy PowerShell với quyền Admin):
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ Lỗi: `pip install GDAL` thất bại
**Cách sửa**:
1. Vào https://github.com/cgohlke/geospatial-wheels/releases
2. Tải file `.whl` đúng version Python:
   - Python 3.12: `GDAL‑3.x.x‑cp312‑cp312‑win_amd64.whl`
   - Python 3.13: `GDAL‑3.x.x‑cp313‑cp313‑win_amd64.whl`
3. Cài:
   ```cmd
   pip install "tên_file.whl"
   ```

---

## 📝 Tóm tắt lệnh cài đặt nhanh

Sau khi đã cài Python, PostgreSQL, PostGIS, OSGeo4W, Git:

```cmd
:: 1. Clone project
git clone -b final https://github.com/DarkinDev/web-gis.git
cd web-gis

:: 2. Tạo venv và cài packages
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

:: 3. Tạo database (chạy trong psql)
:: psql -U postgres
:: CREATE DATABASE bus_gis;
:: \c bus_gis
:: CREATE EXTENSION IF NOT EXISTS postgis;
:: \q

:: 4. Sửa settings.py (mật khẩu DB, đường dẫn GDAL)

:: 5. Migrate và nạp dữ liệu
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/sample_data.json

:: 6. Tạo admin
python manage.py createsuperuser

:: 7. Tạo user mẫu (tùy chọn)
python create_users.py

:: 8. Chạy server
python manage.py runserver
```

---

## 🎉 Hoàn tất!

Truy cập http://127.0.0.1:8000 và tận hưởng hệ thống BusGIS WebGIS! 🚍🗺️

**Tác giả**: DarkinDev  
**Repository**: https://github.com/DarkinDev/web-gis
