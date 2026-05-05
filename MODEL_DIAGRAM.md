# Sơ đồ Model (ERD Diagram) - WebGIS Quản lý Xe buýt

Dưới đây là mã Mermaid mô tả cấu trúc quan hệ giữa các Model trong dự án của bạn. Bạn có thể dùng mã này để dán vào báo cáo hoặc các công cụ vẽ sơ đồ.

```mermaid
classDiagram
    class User {
        +username: String
        +email: String
        +is_staff: Boolean
    }

    class UserProfile {
        +user: OneToOne
        +phone_number: String
    }

    class BusRoute {
        +route_number: String
        +name: String
        +start_point: String
        +end_point: String
        +geometry: LineString (PostGIS)
        +is_active: Boolean
        +is_deleted: Boolean
    }

    class BusStop {
        +name: String
        +code: String
        +location: Point (PostGIS)
        +has_shelter: Boolean
        +is_active: Boolean
    }

    class RouteStop {
        +route: ForeignKey (BusRoute)
        +stop: ForeignKey (BusStop)
        +order: Integer
        +distance_from_start: Decimal
        +estimated_time: Integer
    }

    User "1" -- "1" UserProfile : owns
    BusRoute "1" *-- "many" RouteStop : contains
    BusStop "1" *-- "many" RouteStop : belongs to
```

### Hướng dẫn sử dụng:
1.  **Xem trực tiếp:** Mở file này trong VS Code và nhấn `Ctrl + Shift + V`.
2.  **Xuất file ảnh:** Truy cập [Mermaid Live Editor](https://mermaid.live/), dán đoạn mã trên vào để tải về file ảnh định dạng PNG hoặc SVG rất đẹp và sắc nét cho vào báo cáo Word.
