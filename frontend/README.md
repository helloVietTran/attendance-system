# Frontend Documentation

## Tổng quan
Frontend của hệ thống quản lý nhân sự được xây dựng bằng HTML, CSS và JavaScript thuần. Giao diện sử dụng các component tĩnh và tương tác với backend API qua HTTP requests.

## Cấu hình và Chạy Frontend

### 1. Chạy Frontend trên Localhost:5500
Để tránh lỗi CORS khi kết nối với backend, hãy chạy frontend trên `localhost:5500` thay vì `127.0.0.1:5500`.

#### Bước thực hiện:
1. Mở Visual Studio Code
2. Cài đặt extension "Live Server" nếu chưa có
3. Mở thư mục `frontend` trong VS Code
4. Click chuột phải vào file `base.html` (hoặc file HTML chính) và chọn "Open with Live Server"
5. Hoặc sử dụng command palette: `Ctrl+Shift+P` → "Live Server: Open with Live Server"

Frontend sẽ chạy trên: `http://localhost:5500`

### 2. Cấu hình API URL
Trong các file JavaScript (như `auth.js`, `api.js`), API URL được cấu hình như sau:

```javascript
const API_BASE_URL = "http://localhost:8000/api/v1";
```

Đảm bảo backend đang chạy trên `localhost:8000`.

### 3. Lý do sử dụng localhost:5500 thay vì 127.0.0.1
- **Tránh lỗi CORS**: Khi frontend chạy trên `127.0.0.1:5500` và backend trên `localhost:8000`, trình duyệt có thể coi đây là domain khác nhau, gây ra lỗi CORS (Cross-Origin Resource Sharing).
- **localhost** được coi là domain hợp lệ và tương thích hơn với các chính sách bảo mật của trình duyệt.

### 4. Cấu trúc Thư mục Frontend
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

### 5. Xác thực và Phiên làm việc
- Hệ thống sử dụng cookie session để xác thực
- Không lưu access token trong localStorage
- Frontend gửi requests với `credentials: "include"` để tự động gửi cookie

### 6. Troubleshooting
- **Lỗi CORS**: Đảm bảo frontend chạy trên `localhost:5500` và backend trên `localhost:8000`
- **Không thể kết nối API**: Kiểm tra backend có đang chạy không
- **Session không hoạt động**: Xóa cookie và đăng nhập lại
