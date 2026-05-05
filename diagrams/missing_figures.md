# Danh sách ảnh/sơ đồ: Hiện có & còn thiếu (và tên file đề xuất)

Tệp này liệt kê các ảnh/sơ đồ mà báo cáo cần, trạng thái hiện có (theo `diagrams/images_list.md` / attachments), và tên file đề xuất để bạn export và chèn.

## A. Ảnh UI hiện có (đề xuất đặt trong `images/`)
- `images/home.png` — Màn hình Landing/Home (có trong `images_list.md`)
- `images/routes_list.png` — Danh sách tuyến với map và bảng (có)
- `images/route_detail.png` — Trang chi tiết tuyến (có)
- `images/search_ui.png` — Giao diện tìm tuyến (có)
- `images/import_tool.png` — Giao diện import (admin) (có)
- `images/admin_manage_routes.png` — Dashboard quản trị (có)
- `images/notification_email.png` — Mẫu email (có)

## B. 20 Use Case — đề xuất tên file (nên export từng UC thành ảnh riêng)
Gợi ý đặt tên: `ucXX_<tieu_de_ngan>.png` (không dấu, gạch dưới). Ví dụ:
- `uc01_dang_ky_tai_khoan.png`
- `uc02_dang_nhap.png`
- `uc03_dang_xuat.png`
- `uc04_xem_ban_do.png`
- `uc05_tim_tuyen_theo_vi_tri.png`
- `uc06_tim_tuyen_theo_ma_ten.png`
- `uc07_xem_chi_tiet_tuyen.png`
- `uc08_xem_chi_tiet_tram.png`
- `uc09_danh_dau_yeu_thich.png`
- `uc10_gui_phan_hoi.png`
- `uc11_dat_lai_mat_khau.png`
- `uc12_admin_import_du_lieu.png`
- `uc13_admin_crud_tuyen.png`
- `uc14_admin_crud_tram.png`
- `uc15_khoi_phuc_tuyen_da_xoa.png`
- `uc16_gui_thong_bao.png`
- `uc17_lap_lich_import.png`
- `uc18_xem_lich_su_import.png`
- `uc19_quan_ly_quyen.png`
- `uc20_xuat_du_lieu_tuyen.png`
 - `uc20_xuat_du_lieu_tuyen.png`
 - `uc21_import_excel_routes_stops.png` — Import Excel (Routes & Stops)

## C. Sơ đồ (logic / ERD / Architecture / DFD / Sequence / Activity)
Hiện có các khối mermaid trong `diagrams/combined_diagrams.mmd`. Đề xuất export sang `diagrams/exports/` với tên:
- `er_cac_thuc_the.png` (ERD: Các thực thể)
- `er_mo_rong.png` (ERD mở rộng)
- `architecture_system.png` (Sơ đồ kiến trúc hệ thống)
- `dfd_pipeline.png` (Sơ đồ Luồng xử lý dữ liệu / Import pipeline)
- `usecase_overview.png` (Use Case — Tổng quan)
- `usecase_auth.png` (Use Case — Xác thực)
- `usecase_report.png` (Use Case — Báo cáo sự cố)
- `sequence_search_route.png`
- `sequence_import.png`
- `sequence_notification.png`
- `activity_find_route.png`
- `activity_import.png`
- `activity_registration.png`
- `activity_reset_password.png`

## D. Ảnh test / outputs (nên có để minh chứng kết quả)
- `test_search_result.png` — kết quả tìm tuyến (screenshot test)
- `test_import_report.png` — màn hình báo cáo import (log/errors)
- `export_geojson_sample.png` — ví dụ file export (preview)

## E. Trạng thái & hành động đề xuất
- Bạn đã có: UI screenshots cơ bản (như mục A). Tôi thấy attachment listing có các file `UC01..UC20` — vậy hãy kiểm tra folder `images/` dựa theo tên đề xuất.
- Nếu thiếu: xuất từ `diagrams/combined_diagrams.mmd` bằng `mmdc` vào `diagrams/exports/`, và chụp screenshot UI cập nhật vào `images/`.

## F. Lệnh ví dụ để render mermaid → PNG (mmdc)
PowerShell (giả sử `mmdc` đã cài):
```
mmdc -i diagrams/combined_diagrams.mmd -o diagrams/exports/er_cac_thuc_the.png -b transparent --width 1200
```

Gợi ý: render từng block riêng (hoặc tách file `.mmd` nhỏ) để dễ kiểm soát kích thước và caption.
