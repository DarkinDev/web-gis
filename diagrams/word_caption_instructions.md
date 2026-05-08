# Hướng dẫn chi tiết: Chèn caption và tạo Danh mục Hình / Sơ đồ trong Word (Windows)

Phiên bản: Microsoft Word (Windows). Các bước dưới đây là copy-ready để dán vào `Đề tài.docx` khi bạn thực hiện thủ công.

## A. Tạo caption cho một ảnh / sơ đồ
1. Chèn ảnh vào vị trí mong muốn: `Insert` → `Pictures` → chọn file (hoặc dán ảnh trực tiếp).
2. Chọn ảnh (click vào ảnh) để hiển thị khung quanh.
3. Vào `References` → `Insert Caption`.
4. Nếu chưa có nhãn phù hợp, click `New Label...` và nhập:
   - `Hình` cho ảnh giao diện / screenshot
   - `Sơ đồ` cho sơ đồ logic/kiến trúc/DFD
5. Trong hộp `Caption`, sửa thành định dạng mong muốn, ví dụ: `Hình 2.1: Màn hình Landing / Home`.
6. Để đánh số chương kèm theo (ví dụ Hình 2.1), click `Numbering...` → chọn `Include chapter number` → chọn kiểu Heading level (thường `Heading 1`) → OK.
7. Chọn `Position` = `Below selected item` để caption nằm dưới ảnh.
8. Click `OK` để chèn caption.

Ghi chú: Để Word tự động đánh số theo chương, bạn phải sử dụng style `Heading 1` cho tiêu đề chương (ví dụ: "Chương 2").

## B. Tạo Danh mục Hình / Danh mục Sơ đồ (Table of Figures)
1. Đặt con trỏ tại nơi muốn chèn mục lục (thường trước phần phụ lục hoặc sau mục lục).
2. Vào `References` → `Insert Table of Figures`.
3. Ở `Caption label` chọn nhãn `Hình` (để tạo Danh mục Hình). Chọn định dạng và nhấn `OK`.
4. Lặp lại để chèn Danh mục cho nhãn `Sơ đồ` (chọn `Sơ đồ` trong `Caption label`).

Ghi chú: Khi bạn thêm/xóa hoặc đổi vị trí ảnh, click phải vào Table of Figures → `Update Field` → `Update entire table` để làm mới số trang và mục lục.

## C. Cross-reference (tham chiếu đến ảnh/sơ đồ trong văn bản)
1. Đặt con trỏ tại vị trí muốn chèn tham chiếu (ví dụ: "(xem Hình 2.1)").
2. Vào `References` → `Cross-reference`.
3. `Reference type` chọn `Figure` (tương ứng với `Hình`/`Sơ đồ`).
4. Trong `Insert reference to` chọn `Only label and number` hoặc `Entire caption` tuỳ mục đích.
5. Chọn caption cần tham chiếu trong danh sách rồi nhấn `Insert`.

## D. Lưu ý & kinh nghiệm
- Sử dụng hai nhãn `Hình` và `Sơ đồ` để tách hai loại mục lục.
- Đặt style `Heading 1` cho tiêu đề chương để `Include chapter number` hoạt động đúng.
- Nếu Word bị lỗi mã hoá ký tự tiếng Việt trên Windows, dùng `Save As` → `Word Document (*.docx)` và đảm bảo font chữ Unicode (ví dụ: `Times New Roman`, `Calibri`).
- Để xuất PDF giữ nguyên chất lượng ảnh: `File` → `Export` → `Create PDF/XPS` và kiểm tra `Optimize for: Standard (publishing online and printing)`.

## E. Mẫu caption sẵn sàng (copy-paste)
- Trước ảnh (ví dụ): "Hình dưới đây minh họa giao diện ..."
- Caption (ví dụ): `Hình X.Y: Màn hình Landing / Home của hệ thống.`
- Sau ảnh (ví dụ): "Ảnh cho thấy ... (2–3 câu phân tích)." 
