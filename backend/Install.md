## 🚀 Cài Đặt & Chạy Dự Án

### **Yêu Cầu Hệ Thống**

- **Python**: 3.10 hoặc cao hơn
- **MySQL**: 5.7 hoặc cao hơn

### **1. Clone Dự Án**

```bash
git clone https://github.com/helloVietTran/attendance-system
cd backend
```

### **2. Tạo Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### **3. Cài Đặt Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Cấu Hình Biến Môi Trường**

Tạo file `.env` trong thư mục `backend/`:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/attendance_db
SECRET_KEY=your-secret-key-here
OVERTIME_MONTHLY_LIMIT_MINS=2400  # 40 giờ = 2400 phút
OVERTIME_YEARLY_LIMIT_MINS=12000  # 200 giờ = 12000 phút
```

### **5. Khởi Tạo Database**

```bash
# Chạy script init SQL
mysql -u root -p < init.sql

# Hoặc chạy từ Python
python -c "from app.db.session import init_db; init_db()"
```

### **6. Chạy Server**

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: **http://localhost:8000**

- API Docs: **http://localhost:8000/docs** (Swagger UI)
- ReDoc: **http://localhost:8000/redoc**

---

## 📁 Cấu Trúc Thư Mục

```
backend/
├── app/
│   ├── api/v1/                    # Các API endpoints
│   │   ├── absence.py            # API quản lý ngày nghỉ
│   │   ├── admin.py              # API admin
│   │   ├── attendance.py         # API chấm công
│   │   ├── auth.py               # API authenticate
│   │   ├── calendar.py           # API lịch làm việc
│   │   ├── employee.py           # API nhân viên
│   │   ├── face_auth.py          # API nhận dạng khuôn mặt
│   │   ├── overtime.py           # API giờ làm thêm
│   │   ├── payroll.py            # API tính lương
│   │   ├── shift.py              # API ca làm việc
│   │   └── ...
│   ├── models/                    # Các model database
│   │   ├── employee.py
│   │   ├── attendance_log.py
│   │   ├── overtime_request.py
│   │   └── ...
│   ├── schemas/                   # Pydantic schemas
│   │   ├── employee.py
│   │   ├── attendance_log.py
│   │   └── ...
│   ├── services/                  # Business logic
│   │   ├── attendance_service.py
│   │   ├── overtime_service.py
│   │   ├── payroll_service.py
│   │   ├── face_recognition_service.py
│   │   └── ...
│   ├── core/                      # Config & utils
│   │   ├── config.py
│   │   ├── dependency.py
│   │   ├── exception.py
│   │   └── scheduler.py
│   ├── db/                        # Database
│   │   └── session.py
│   └── main.py                    # Điểm khởi động
├── tests/                          # Unit tests
├── init.sql                        # Script khởi tạo DB
├── requirements.txt               # Dependencies
├── pytest.ini                      # Cấu hình pytest
└── README.md
```

---

## 🧪 Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Chạy tests cụ thể
pytest tests/api/v1/test_attendance.py

# Chạy với verbose output
pytest -v

# Chạy với coverage
pytest --cov=app
```

---
