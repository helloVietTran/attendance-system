# Frontend Documentation

## Tổng quan
Frontend của hệ thống quản lý nhân sự được xây dựng bằng HTML, CSS và JavaScript thuần. Giao diện sử dụng các component tĩnh và tương tác với backend API qua HTTP requests.

## Lưu ý khi call API
- Hệ thống hiện tại sử dụng **JWT** để xác thực thay vì session server-side.
- Access token được lưu trong `localStorage` với key `access_token`.
- Khi gọi request tới backend, hãy dùng helper `fetchWithAuth(url, options)` trong `frontend/core/js/api.js`.
- `fetchWithAuth` sẽ tự động thêm header `Authorization: Bearer <token>` và `Content-Type: application/json`.

## Chạy frontend
1. Mở Visual Studio Code
2. Cài đặt extension "Live Server" nếu chưa có
3. Mở thư mục `frontend` trong VS Code
4. Click chuột phải vào file `base.html` (hoặc file HTML chính) và chọn "Open with Live Server"
5. Hoặc sử dụng command palette: `Ctrl+Shift+P` → "Live Server: Open with Live Server"

## Cấu trúc Thư mục Frontend
```
frontend/
├── core/
│   ├── css/
│   │   └── main.css          # CSS chính
│   ├── js/
│   │   ├── api.js            # Hàm gọi API chung
│   │   ├── auth.js           # Xử lý xác thực
│   │   └── router.js         # Điều hướng trang
│   └── layout/
│       ├── base.html         # Layout chính
│       ├── header.html       # Header
│       └── sidebar.html      # Sidebar
├── pages/
│   ├── Authentication/
│   │   ├── auth.css
│   │   ├── auth.js
│   │   └── login.html        # Trang đăng nhập
│   ├── Dashboard/
│   │   ├── dashboard.css
│   │   ├── dashboard.js
│   │   └── index.html        # Trang dashboard
│   ├── Reports/
│   │   ├── attendance.html
│   │   ├── reports-main.js
│   │   └── reports.css
│   └── Setting/
│       ├── setting_system.html
│       ├── setting_time_tracking.html
│       ├── setting.css
│       ├── setting.html
│       └── setting.js
└── README.md                 # Tài liệu này
```
