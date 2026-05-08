**Hướng Dẫn & Mục Lục Sơ Đồ**

- **Mục lục (Sơ đồ):**
  - **Diagram 1:** Use Case tổng quan ([diagrams/usecase_system.mmd](diagrams/usecase_system.mmd))
  - **Diagram 2:** Use Case - Authentication ([diagrams/usecase_auth.mmd](diagrams/usecase_auth.mmd))
  - **Diagram 3:** Activity - Tìm tuyến ([diagrams/activity_search_route.mmd](diagrams/activity_search_route.mmd))
  - **Diagram 4:** Activity - Import dữ liệu tuyến ([diagrams/activity_import_bus_data.mmd](diagrams/activity_import_bus_data.mmd))
  - **Diagram 5:** Activity - Đăng ký người dùng ([diagrams/activity_user_registration.mmd](diagrams/activity_user_registration.mmd))
  - **Diagram 6:** Sequence - Tìm tuyến ([diagrams/sequence_search_route.mmd](diagrams/sequence_search_route.mmd))
  - **Diagram 7:** Sequence - Job import tuyến ([diagrams/sequence_import_job.mmd](diagrams/sequence_import_job.mmd))
  - **Diagram 8:** Sequence - Gửi thông báo ([diagrams/sequence_notification.mmd](diagrams/sequence_notification.mmd))
  - **Diagram 9:** ERD hệ thống ([diagrams/erd.mmd](diagrams/erd.mmd))

- **Mục lục (Hình ảnh):**
  - images/home.png — màn hình Landing/Home
  - images/routes_list.png — danh sách tuyến/Map + list
  - images/route_detail.png — trang chi tiết tuyến với bản đồ
  - images/search_ui.png — giao diện tìm tuyến và kết quả
  - images/import_tool.png — UI import (admin)
  - images/notification_email.png — mẫu email thông báo
  - images/admin_manage_routes.png — trang quản lý tuyến (admin)

Hướng dẫn chèn vào báo cáo:
- Tạo phần **Sơ đồ** (một chương/tiêu đề riêng). Với mỗi sơ đồ, dán mã Mermaid bên trong block code hoặc nhúng bản vẽ đã render (SVG/PNG). Đánh nhãn dạng "Sơ đồ 1.1: Tên sơ đồ" — KHÔNG chèn ảnh chụp sơ đồ thay cho sơ đồ; ảnh chỉ dùng cho minh họa UI.
- Tạo phần **Hình ảnh** (một chương/tiêu đề riêng). Tất cả ảnh screenshot UI đặt ở đây, đánh nhãn "Hình 2.1: Mô tả".
- Tham chiếu: trong phần phân tích, tham chiếu chung theo cả hai: "(Xem Sơ đồ 1.1)" cho diagram, "(Xem Hình 2.1)" cho ảnh.

Lưu ý kỹ thuật:
- Sử dụng Mermaid để render `.mmd` -> SVG/PNG (ví dụ: `mmdc -i file.mmd -o file.svg`).
- Nếu cần, tôi có thể xuất từng sơ đồ ra `svg` hoặc `png` và đưa vào `diagrams/exports/`.

Tiếp theo: các file `.mmd` chứa mã Mermaid cho từng sơ đồ đã được tạo trong thư mục `diagrams`.
