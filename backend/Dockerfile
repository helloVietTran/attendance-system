FROM python:3.11-slim
WORKDIR /app

# Cài đặt thư viện hệ thống cho mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ folder app vào container
COPY . .

# App chạy tại thư mục backend, main.py nằm trong backend/app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]