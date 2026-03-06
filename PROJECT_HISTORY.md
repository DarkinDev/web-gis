# Lịch Sử Phát Triển Dự Án WebGIS Quản Lý Xe Buýt

Tài liệu này tổng hợp toàn bộ quá trình phát triển, các tính năng đã thực hiện và lịch sử thay đổi (changelog) của dự án WebGIS Bus Management.

## 1. Tổng Quan Dự Án
*   **Tên dự án**: Bus Management WebGIS
*   **Mục tiêu**: Xây dựng ứng dụng web quản lý hệ thống xe buýt công cộng, tích hợp bản đồ số và các công cụ phân tích không gian (GIS).
*   **Công nghệ sử dụng**:
    *   **Backend**: Python, Django, Django REST Framework, GeoDjango.
    *   **Database**: PostgreSQL 18, PostGIS (cho dữ liệu không gian).
    *   **Frontend**: HTML5, CSS3, JavaScript, LeafletJS (bản đồ), Bootstrap 5 (giao diện).
    *   **Tools**: OSGeo4W (thư viện GDAL/GEOS cho Windows).

## 2. Các Tính Năng Đã Hoàn Thiện

### A. Quản Lý Dữ Liệu (Backend & Database)
*   **Cấu hình GeoDjango**: Tích hợp thư viện GDAL/GEOS từ OSGeo4W để xử lý dữ liệu địa lý trên Windows.
*   **Database Schema**:
    *   `BusRoute`: Lưu trữ thông tin tuyến xe (Số hiệu, tên, lộ trình dạng LineString, màu sắc...).
    *   `BusStop`: Lưu trữ trạm dừng (Tên, toạ độ dạng Point, địa chỉ...).
    *   `RouteStop`: Bảng trung gian quản lý thứ tự các trạm trên một tuyến (Có khoảng cách, thời gian dự kiến).
*   **API**:
    *   Cung cấp API định dạng GeoJSON cho các lớp dữ liệu Bản đồ (Routes, Stops).
    *   API tìm kiếm, lọc dữ liệu.

### B. Chức Năng GIS (Phân Tích Không Gian)
*   **Tìm trạm gần nhất (Nearest Neighbor)**: Tìm các trạm xe buýt trong phạm vi gần vị trí người dùng nhất.
*   **Vùng phục vụ (Buffer)**: Tạo vùng đệm (buffer) quanh trạm dừng với bán kính tùy chỉnh (ví dụ: 500m) để xem khu vực được phục vụ.
*   **Tìm đường đi (Routing)**: Tìm các tuyến xe buýt kết nối giữa hai trạm dừng bất kỳ.
*   **Tính khoảng cách**: Tính toán khoảng cách thực tế giữa các điểm.

### C. Giao Diện Người Dùng (Frontend)
*   **Bản đồ tương tác**: Hiển thị trực quan các tuyến xe và trạm dừng trên nền bản đồ OpenStreetMap.
*   **Tìm kiếm thông minh**: Tìm kiếm trạm dừng và tuyến xe theo tên.
*   **Công cụ GIS trên web**: Giao diện cho phép người dùng chọn điểm đi/đến, tạo vùng đệm trực quan ngay trên trình duyệt.
*   **Responsive**: Giao diện tương thích với cả máy tính và điện thoại.

---

## 3. Nhật Ký Thay Đổi (Commit History)

Dưới đây là danh sách chi tiết các thay đổi (commits) có thể sử dụng để ghi lại lịch sử phát triển trên Git:

### Giai Đoạn 1: Khởi Tạo Dự Án (Initialization)
*   `init`: Khởi tạo Django project `bus_management`.
*   `config`: Cấu hình `settings.py` cho database PostgreSQL và PostGIS.
*   `fix`: Cập nhật đường dẫn GDAL/GEOS cho môi trường Windows (OSGeo4W).

### Giai Đoạn 2: Xây Dựng Cơ Sở Dữ Liệu (Database & Models)
*   `feat(models)`: Tạo models `BusRoute`, `BusStop` với các trường địa lý (`LineStringField`, `PointField`).
*   `feat(models)`: Tạo model liên kết `RouteStop` để quản lý lộ trình.
*   `chore(db)`: Chạy migrations khởi tạo schema database.
*   `chore(admin)`: Đăng ký models vào Django Admin, tạo Superuser.

### Giai Đoạn 3: Phát Triển API & GIS Logic (Backend)
*   `feat(api)`: Cài đặt Django REST Framework và `rest_framework_gis`.
*   `feat(serializers)`: Tạo Serializers chuyển đổi dữ liệu models sang GeoJSON.
*   `feat(views)`: Viết các view API cơ bản (List, Detail) cho Routes và Stops.
*   `feat(gis)`: Implement thuật toán tìm trạm gần nhất (`Distance`, `order_by`).
*   `feat(gis)`: Implement thuật toán tạo vùng đệm (`buffer`) và tìm kiếm trong vùng (`within`).
*   `feat(gis)`: Implement logic tìm tuyến đi giữa 2 trạm (Route Finding).

### Giai Đoạn 4: Giao Diện & Tích Hợp (Frontend)
*   `feat(ui)`: Thiết lập cấu trúc templates HTML và tích hợp Bootstrap 5.
*   `feat(map)`: Tích hợp thư viện LeafletJS, hiển thị bản đồ nền OSM.
*   `feat(js)`: Viết `map.js` để fetch dữ liệu từ API và vẽ lên bản đồ.
*   `feat(ui)`: Thêm thanh Sidebar điều khiển, ô tìm kiếm và menu chức năng.
*   `feat(ux)`: Thêm tương tác click vào trạm/tuyến để xem thông tin chi tiết (Popups).
*   `feat(ui)`: Hoàn thiện giao diện trang chủ, trang danh sách tuyến và chi tiết tuyến.

### Giai Đoạn 5: Hoàn Thiện & Dữ Liệu (Finalization)
*   `chore(data)`: Viết management command `populate_bus_data.py` để nạp dữ liệu mẫu (Tuyến 01, 152 tại TP.HCM).
*   `fix(settings)`: Tinh chỉnh cấu hình static files và template paths.
*   `docs`: Cập nhật tài liệu dự án và hướng dẫn cài đặt.

---

## 4. Hướng Dẫn Cập Nhật Code (Dành cho Dev)
1.  **Chạy server**: `python manage.py runserver`
2.  **Tạo migrations mới** (nếu sửa models):
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
3.  **Reset dữ liệu mẫu**:
    ```bash
    python manage.py populate_bus_data
    ```
