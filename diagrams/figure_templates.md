# Mẫu văn bản trước / caption / sau cho ảnh và sơ đồ

Tập hợp mẫu văn bản để copy-paste vào `Đề tài.docx` trước khi chèn ảnh, caption (dưới ảnh) và phần mô tả/ghi chú sau ảnh. Thay `X.Y` bằng số chương/mục tương ứng trong báo cáo của bạn.

---

## Hướng dẫn ngắn
- Trước ảnh: 2–4 câu giới thiệu bối cảnh và mục tiêu ảnh.
- Chú thích (caption): `Hình X.Y: <Tiêu đề ngắn>` hoặc `Sơ đồ X.Y: <Tiêu đề>` cho sơ đồ.
- Sau ảnh: 2–4 câu phân tích, nêu điểm chính và kết luận/nghị xuất.

---

## 1. Ảnh giao diện chính (Landing/Home)
- Trước ảnh: "Hình dưới đây minh hoạ giao diện trang chủ của hệ thống, nơi người dùng có thể truy cập tính năng tìm tuyến, xem thông báo và đăng nhập/đăng ký. Giao diện tối ưu cho cả desktop và mobile, hiển thị bản đồ làm trung tâm."
- Chú thích: "Hình X.Y: Màn hình Landing / Home của hệ thống"
- Sau ảnh: "Giao diện tập trung vào bản đồ giúp người dùng nhanh chóng định vị tuyến. Lưu ý: cần kiểm tra trải nghiệm trên màn hình nhỏ và độ tương phản màu cho các lớp đường." 

## 2. Ảnh danh sách tuyến (routes_list.png)
- Trước ảnh: "Danh sách tuyến kết hợp bảng và bản đồ cung cấp cả cái nhìn tổng quan và chi tiết từng tuyến. Người dùng có thể lọc, sắp xếp và nhấp vào một tuyến để xem chi tiết."
- Chú thích: "Hình X.Y: Danh sách tuyến — bản đồ và bảng tương tác"
- Sau ảnh: "Bảng cho phép so sánh thuộc tính tuyến (mã, tên, trạng thái) trong khi bản đồ cung cấp bối cảnh không gian. Kiến nghị: bổ sung lọc theo khu vực và trạng thái hoạt động." 

## 3. Ảnh chi tiết tuyến (route_detail.png)
- Trước ảnh: "Trang chi tiết tuyến hiển thị lộ trình, danh sách trạm theo thứ tự và thông tin lịch trình liên quan."
- Chú thích: "Hình X.Y: Trang chi tiết tuyến — lộ trình và trạm"
- Sau ảnh: "Tối ưu hiển thị thông tin trạm (khoảng cách, mã trạm) và liên kết nhanh để báo cáo sự cố hoặc thêm vào yêu thích." 

## 4. Ảnh giao diện tìm tuyến (search_ui.png)
- Trước ảnh: "Giao diện tìm kiếm hỗ trợ tìm theo vị trí hiện tại, mã/tên tuyến, hoặc bộ lọc nâng cao."
- Chú thích: "Hình X.Y: Giao diện tìm tuyến và bộ lọc"
- Sau ảnh: "Hai chế độ tìm (vị trí và từ khoá) giúp phục vụ cả người đi trong khu vực và người tìm tuyến cụ thể. Đề xuất: thêm gợi ý tự động (autocomplete) cho tên/mã tuyến." 

## 5. Ảnh import tool (import_tool.png)
- Trước ảnh: "Giao diện upload/import dữ liệu dành cho quản trị viên, cho phép upload file CSV/JSON và kiểm tra schema trước khi enqueue job xử lý."
- Chú thích: "Hình X.Y: Công cụ import dữ liệu (Admin)"
- Sau ảnh: "Quy trình import nên hiển thị rõ trạng thái validate, lỗi từng dòng, và preview trước khi chạy. Khuyến nghị thêm chế độ dry-run." 

## 6. Ảnh Dashboard quản trị (admin_manage_routes.png)
- Trước ảnh: "Dashboard quản trị hiển thị danh sách tuyến, công cụ CRUD, và thông tin audit cơ bản."
- Chú thích: "Hình X.Y: Dashboard Admin — quản lý tuyến và trạm"
- Sau ảnh: "Cần cơ chế xác nhận khi xóa (soft-delete) và truy vấn lịch sử thay đổi. Gợi ý hiển thị nhanh trạng thái import gần nhất." 

## 7. Ảnh mẫu email (notification_email.png)
- Trước ảnh: "Mẫu email HTML dùng để gửi thông báo thay đổi tuyến, khôi phục mật khẩu hoặc thông báo import."
- Chú thích: "Hình X.Y: Mẫu email thông báo"
- Sau ảnh: "Kiểm tra hiển thị trên nhiều client mail; tách rõ tiêu đề và nội dung tóm tắt để người nhận hiểu ngay ý chính." 

---

## 8. Use Case — Tổng quan (sơ đồ usecase tổng)
- Trước sơ đồ: "Sơ đồ sau trình bày các actor chính và các ca sử dụng cốt lõi của hệ thống, giúp định nghĩa phạm vi chức năng cho thiết kế và kiểm thử."
- Chú thích: "Sơ đồ X.Y: Use Case — Tổng quan chức năng hệ thống"
- Sau sơ đồ: "Từ sơ đồ này, tách các luồng chính phục vụ người dùng (tìm tuyến, xem chi tiết) và quản trị (import, quản lý). Sơ đồ cũng dùng để định nghĩa kịch bản kiểm thử end-to-end." 

## 9. Use Case — Xác thực (đăng ký / đăng nhập)
- Trước sơ đồ: "Sơ đồ mô tả luồng xác thực: đăng ký, xác nhận email, đăng nhập, và đặt lại mật khẩu."
- Chú thích: "Sơ đồ X.Y: Use Case — Xác thực và quản lý hồ sơ"
- Sau sơ đồ: "Lưu ý bảo mật: giới hạn rate, hash mật khẩu, và token expiring; xác minh email trước khi cấp quyền." 

## 10. 20 Use Case chi tiết (mỗi UC riêng)
Lưu ý: cho từng ảnh UC01..UC20 (nếu bạn đã export từng UC thành ảnh), dùng cùng mẫu:
- Trước ảnh: mô tả ngữ cảnh UC (3 câu) — ví dụ: "UC01: Người dùng mới đăng ký bằng email; hệ thống tạo account, gửi email xác nhận và kích hoạt sau xác thực."
- Chú thích: "Hình X.Y: UC01 — Đăng ký tài khoản"
- Sau ảnh: nêu flow chính, biến thể lỗi chính (e.g., email trùng), và điểm kiểm thử chính.

*(Gợi ý: export từng UC bằng tên `UC01_Đăng_ky.png`, `UC02_Đăng_nhap.png`, ... để dễ map vào báo cáo.)*

---

## 11. ERD (Entities Relationship Diagram)
- Trước sơ đồ: "Sơ đồ ERD mô tả các thực thể chính (User, UserProfile, BusRoute, BusStop, RouteStop, ImportJob, AuditLog, Notification) và quan hệ giữa chúng."
- Chú thích: "Sơ đồ X.Y: Sơ đồ ERD — các thực thể chính và quan hệ"
- Sau sơ đồ: "Ghi chú về ràng buộc quan hệ, chỉ mục cần thiết (ví dụ: GIST index trên cột geometry), và chiến lược soft-delete/restore." 

## 12. ERD mở rộng (thực thể phụ / audit / import)
- Trước sơ đồ: "ERD mở rộng bao gồm các bảng audit, import_job và các trường báo cáo chi tiết phục vụ debug/rollback."
- Chú thích: "Sơ đồ X.Y: ERD — mô tả chi tiết thực thể phụ"
- Sau sơ đồ: "Đề xuất cài đặt bảng audit để lưu diff và user thực hiện; import_job lưu report dạng text/JSON cho traceability." 

## 13. Sơ đồ kiến trúc hệ thống (architecture)
- Trước sơ đồ: "Sơ đồ kiến trúc mô tả client, edge (CDN, LB), app layer (Django, Celery, Redis), và data layer (Postgres+PostGIS, TileServer)."
- Chú thích: "Sơ đồ X.Y: Kiến trúc hệ thống — thành phần và luồng dữ liệu"
- Sau sơ đồ: "Nêu các điểm cần tối ưu: caching (Redis), queue cho xử lý nặng, storage cho ảnh gốc, và chiến lược scaling cho PostGIS." 

## 14. Sơ đồ Luồng xử lý dữ liệu (DFD / Pipeline / Import)
- Trước sơ đồ: "Sơ đồ này mô tả quá trình ingest, validate, enqueue, xử lý, upsert vào PostGIS và send-notify; nhấn nơi cần retry/alert."
- Chú thích: "Sơ đồ X.Y: Luồng xử lý dữ liệu (Import / ETL Pipeline)"
- Sau sơ đồ: "Nhấn mạnh tách ingestion và processing qua queue; lưu temp file để debug; cập nhật spatial index sau batch upsert; và tạo import report cho admin." 

## 15. Sequence diagrams (ví dụ: tìm tuyến, import job, notify)
- Trước sơ đồ: "Mô tả trình tự tin nhắn giữa client → API → worker → DB/EmailSvc cho kịch bản cụ thể."
- Chú thích: "Sơ đồ X.Y: Sequence — <tên kịch bản>"
- Sau sơ đồ: "Ghi rõ timeout, retry policy, và các điểm có thể gây blocking (ví dụ: long-running DB transaction)." 

## 16. Activity diagrams (ví dụ: user registration, import)
- Trước sơ đồ: "Diagram hoạt động (activity) mô tả bước thứ tự thủ tục nghiệp vụ (ví dụ: đăng ký, đặt lại mật khẩu, import)."
- Chú thích: "Sơ đồ X.Y: Activity — <tên quy trình>"
- Sau sơ đồ: "Nêu các branch quan trọng (success / validation error / retry) và các control decisions cần log/alert." 

## 17. Ảnh khác (screenshot test, lỗi, export CSV)
- Trước ảnh: mô tả mục tiêu chụp (ví dụ: kết quả test, export file mẫu)."
- Chú thích: "Hình X.Y: <mô tả ngắn>"
- Sau ảnh: "Giải thích ý nghĩa, bước tái hiện lỗi (nếu là lỗi) hoặc hướng dẫn dùng file export." 

---

## Mẹo số hóa caption & số ảnh
- Sử dụng caption dạng "Hình X.Y: ..." cho các ảnh giao diện và "Sơ đồ X.Y: ..." cho sơ đồ logic/kiến trúc.
- Nếu bạn cần tự động đánh số, dùng chức năng `References → Insert Caption` trong Word và tạo hai danh mục: `Hình` và `Sơ đồ`.

---

Nếu bạn muốn, tôi sẽ tiếp tục tạo (1) file chứa tất cả caption chính xác cho từng ảnh hiện có (theo tên file), và (2) hướng dẫn từng bước chèn caption + tạo Danh mục Hình/Sơ đồ trong Word.
