# Hướng dẫn cài đặt PostGIS trên Windows

## Vấn đề hiện tại

Django migrations đã chạy được một phần nhờ workaround, nhưng khi tạo các bảng có GIS fields (geometry), PostgreSQL báo lỗi vì không có kiểu dữ liệu `geometry`. Điều này xảy ra vì **PostGIS extension chưa được cài đặt**.

## Giải pháp: Cài đặt PostGIS

### Cách 1: Dùng Stack Builder (Khuyến nghị - Dễ nhất)

1. **Mở Stack Builder**
   - Tìm trong Start Menu: `PostgreSQL 13` → `Application Stack Builder`
   - Hoặc chạy: `C:\Program Files\PostgreSQL\13\bin\stackbuilder.exe`

2. **Chọn PostgreSQL Server**
   - Chọn PostgreSQL 13 từ danh sách
   - Click **Next**

3. **Chọn PostGIS**
   - Tìm và chọn **PostGIS Bundle for PostgreSQL 13**
   - Click **Next** và làm theo hướng dẫn cài đặt

4. **Sau khi cài xong**
   ```bash
   python create_db.py
   ```
   Hoặc chạy SQL trong pgAdmin:
   ```sql
   \c bus_gis
   CREATE EXTENSION postgis;
   ```

5. **Chạy migrations**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Cách 2: Tải PostGIS riêng

1. **Tải PostGIS**
   - Truy cập: https://postgis.net/windows_downloads/
   - Chọn phiên bản phù hợp với PostgreSQL 13 của bạn
   - Tải file installer (ví dụ: `postgis-bundle-pg13x64-setup.exe`)

2. **Cài đặt**
   - Chạy installer
   - Chọn cùng thư mục với PostgreSQL 13
   - Làm theo hướng dẫn

3. **Bật extension**
   ```bash
   python create_db.py
   ```
   Hoặc trong pgAdmin:
   ```sql
   \c bus_gis
   CREATE EXTENSION postgis;
   ```

4. **Chạy migrations**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Cách 3: Dùng pgAdmin (Nếu đã có PostGIS nhưng chưa bật)

1. **Mở pgAdmin**
2. **Kết nối vào server PostgreSQL**
3. **Mở database `bus_gis`**
4. **Chạy SQL Query:**
   ```sql
   CREATE EXTENSION postgis;
   ```
5. **Kiểm tra:**
   ```sql
   SELECT PostGIS_version();
   ```

## Sau khi cài PostGIS

1. **Xóa workaround** (tùy chọn):
   - Xóa file `bus_management/apps.py` (hoặc xóa phần patch)
   - Xóa `bus_management` khỏi `INSTALLED_APPS` đầu tiên trong `settings.py`

2. **Chạy migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Chạy server:**
   ```bash
   python manage.py runserver
   ```

## Kiểm tra PostGIS đã hoạt động

Chạy trong pgAdmin hoặc psql:
```sql
SELECT PostGIS_version();
```

Nếu trả về version (ví dụ: `3.3.2`), PostGIS đã được cài đặt thành công!

## Lưu ý

- **PostGIS là bắt buộc** cho project này vì sử dụng GIS fields (geometry, point, linestring)
- Workaround hiện tại chỉ cho phép migrations chạy một phần, nhưng không thể tạo các bảng GIS
- Sau khi cài PostGIS, mọi thứ sẽ hoạt động bình thường
