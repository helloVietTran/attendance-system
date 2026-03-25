# Hướng dẫn setup Python 3.14.3 + VS Code + Virtual Environment

---

## 🧩 1. Cài Extension Python cho VS Code


* Tìm extension **Python (Microsoft)** → Install
---

## 2. Cài Python

Phiên bản dự án đang dùng: `Python 3.14.3`

Tóm tắt các bước tải:

* cài Python từ python.org
* tick vào **"Add to PATH"**

---

## 📁 3. Clone project

```bash
git clone -b backend https://github.com/helloVietTran/attendance-system
cd backend
```

---

## 4. Tạo môi trường ảo (virtual environment)

### Dùng lệnh sau tạo môi trường ảo:

```bash
python -m venv venv
```

👉 Sau khi chạy sẽ có folder:

```
venv/
```

### Chạy môi trường ảo:

```bash
venv\Scripts\activate
```

👉 Nếu thành công sẽ thấy:

```
(venv) C:\...
```

---

---

## 📦 5. Cài thư viện (ví dụ FastAPI)

```bash
    pip install -r requirements.txt
```

---

## 🚀 6. Chạy ứng dụng Python


```bash
uvicorn main:app --reload
```
