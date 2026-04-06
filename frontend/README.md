# Frontend Real - Hướng Dẫn Lập Trình

## Cấu trúc thư mục

```
frontend-real/
├── login.html             # Trang đăng nhập
├── daily_reports.html     # Trang báo cáo công hàng ngày
├── notifications.html     # Trang thông báo
├── css/
│   ├── login.css          # CSS cho trang đăng nhập
│   └── main.css           # CSS chung cho toàn bộ ứng dụng
├── js/
│   ├── constant.js        # Hằng số API (BASE_URL, API_PREFIX, API_URL)
│   ├── login.js           # Logic xử lý đăng nhập
│   ├── shared.js          # Các hàm dùng chung (checkAuth, logout, showMessage)
│   └── api.js             # Các hàm gọi API (fetchWithAuth)
```

## Giải thích các file

### Root Files
- `login.html` - Trang đăng nhập, form email/password
- `daily_reports.html` - Trang xem báo cáo công hàng ngày
- `notifications.html` - Trang xem thông báo

### CSS Files
- `css/login.css` - Styling riêng cho trang login
- `css/main.css` - CSS chung, variables, layout cơ bản

### JS Files
- `js/constant.js` - Định nghĩa URL API
- `js/login.js` - Xử lý đăng nhập, gọi API login
- `js/shared.js` - Hàm dùng chung: checkAuth(), logout(), showMessage()
- `js/api.js` - Hàm fetchWithAuth() để gọi API có authentication

## Thứ tự import khi thêm file mới

Khi tạo trang HTML mới, import theo thứ tự này:

```html
<script src="../js/constant.js"></script>     <!-- 1. Constants trước -->
<script src="../js/shared.js"></script>       <!-- 2. Shared functions -->
<script src="../js/api.js"></script>          <!-- 3. API functions -->
<script src="./your-page.js"></script>        <!-- 4. Page logic cuối -->
```

## Sửa menu item

Menu được định nghĩa trong HTML của từng trang. Để sửa menu:

1. Mở file HTML của trang
2. Tìm phần menu/sidebar
3. Sửa text và href của menu item

Ví dụ:
```html
<a href="./daily_reports.html">Báo cáo công</a>
```

## Gọi API dùng fetchWithAuth

Sử dụng hàm `fetchWithAuth()` từ `js/api.js`:

```javascript
// GET request
const response = await fetchWithAuth(`${API_URL}/endpoint`);
const data = await response.json();

// POST request
const response = await fetchWithAuth(`${API_URL}/endpoint`, {
    method: 'POST',
    body: JSON.stringify({ key: 'value' })
});
const data = await response.json();

// Hàm tự động thêm Authorization header với token từ localStorage
```