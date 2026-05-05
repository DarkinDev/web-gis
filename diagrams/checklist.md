# Checklist: Render, chèn và kiểm tra ảnh / sơ đồ cho báo cáo

Đây là checklist từng bước để bạn thực hiện: render sơ đồ, lưu ảnh, chèn vào Word, gán caption và tạo danh mục.

1) Chuẩn bị thư mục
   - Tạo `diagrams/exports/` để lưu PNG/SVG xuất từ Mermaid.
   - Tạo `images/` để lưu screenshot giao diện UI.

2) Render sơ đồ Mermaid → PNG/SVG
   - Tách block mermaid lớn nếu cần, render từng sơ đồ riêng.
   - Ví dụ (PowerShell):
     ```powershell
     mmdc -i diagrams/usecase_system.mmd -o diagrams/exports/usecase_overview.png --width 1200
     mmdc -i diagrams/erd.mmd -o diagrams/exports/er_cac_thuc_the.png --width 1400
     ```
   - Kiểm tra file `diagrams/exports/` sau khi render.

3) Chuẩn bị screenshots UI
   - Chụp màn hình với kích thước tối thiểu 1200x800.
   - Đổi tên file theo chuẩn (ví dụ: `home.png`, `routes_list.png`).

4) Chèn vào Word (`Đề tài.docx`)
   - Mở file, đi tới vị trí chèn theo mapping trong `diagrams/images_list.md`.
   - Insert → Picture → chọn file từ `images/` hoặc `diagrams/exports/`.
   - Dùng `diagrams/word_caption_instructions.md` để chèn caption chính xác.

5) Tạo Danh mục Hình / Sơ đồ
   - Vào `References` → `Insert Table of Figures` cho nhãn `Hình` và sau đó cho `Sơ đồ`.

6) Kiểm tra cuối cùng
   - Update all fields: `Ctrl+A` → `F9` để cập nhật toàn bộ cross-references, table of contents và danh mục hình.
   - Kiểm tra font Unicode, khoảng trắng và alignment caption.
   - Xuất PDF kiểm tra chất lượng ảnh.

7) Ghi chú versioning
   - Lưu bản sao `Đề tài_backup_v1.docx` trước khi chèn hàng loạt.
