# AWS EC2 + Docker + CI/CD + HTTPS Deployment Notes

## 1. Chuẩn bị AWS

### IAM User Permissions

Cấp các quyền cần thiết:

* AmazonECS_FullAccess
* AmazonEC2ContainerRegistryFullAccess
* AmazonRDSFullAccess
* IAMFullAccess
* AmazonEC2FullAccess
* AmazonDirectoryServiceFullAccess
* ec2:CreateKeyPair
A
### EC2 Free Tier

Các instance có thể sử dụng:

* t3.micro
* t3.small
* t4g.micro (ARM)
* t4g.small (ARM)
* c7i-flex.large
* m7i-flex.large

---

## 2. Khởi tạo EC2 Server

### Thông tin hệ thống

```text
OS: Ubuntu
Instance: t3.small
```

### Security Group

Mở các cổng:

| Port | Mục đích |
| ---- | ----------- |
| 80   | HTTP        |
| 443  | HTTPS       |
| 8080 | Backend API |

---

## 3. Gán Elastic IP

Để tránh việc IP thay đổi sau mỗi lần restart:

1. EC2 → Elastic IPs
2. Allocate Elastic IP
3. Associate Elastic IP
4. Gắn với EC2 instance

---

## 4. Kết nối RDS MySQL

```bash
docker run --rm -it mysql:8 mysql -h <RDS_ENDPOINT> -P 3306 -u <USER> \ -p
```

---

## 5. SSH vào EC2

```bash
ssh -i "my-aws-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

---

# 6. Cài đặt môi trường

## Docker

```bash
sudo apt update && sudo apt upgrade -y

curl -fsSL https://get.docker.com -o get-docker.sh

sudo sh get-docker.sh
```

## Docker Compose

```bash
sudo apt install docker-compose-plugin -y
```

## Git

```bash
sudo apt install git -y
```

---

# 7. Clone Source Code

```bash
git clone https://github.com/<username>/<repo>.git

cd <repo>
```

---

# 8. Chuẩn bị Model AI (InsightFace)

Do EC2 nhỏ dễ bị thiếu RAM khi tải model.

## Tạo thư mục

```bash
mkdir -p backend/models
```

## Cài unzip

```bash
sudo apt update
sudo apt install -y unzip
```

## Download model

```bash
wget https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_s.zip
```

## Giải nén

```bash
unzip buffalo_s.zip -d backend/models
```

---

# 9. Tạo file .env

```env
TZ=Asia/Ho_Chi_Minh

DB_HOST=<RDS_HOST>
DB_USER=<DB_USER>
DB_PASSWORD=<DB_PASSWORD>
DB_NAME=<DB_NAME>
DB_PORT=3306

SECRET_KEY=<SECRET_KEY>

OVERTIME_DAILY_LIMIT_MINS=240
OVERTIME_MONTHLY_LIMIT_MINS=2400
OVERTIME_YEARLY_LIMIT_MINS=12000
```

---

# 10. Cấu hình Nginx cho Frontend

Mặc định nginx tìm:

```text
index.html
```

Nếu project sử dụng:

```text
login.html
```

thì cần cấu hình:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index login.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

# 11. Docker Compose cơ bản

```yaml
version: '3.8'

services:
  backend:
    build: ./backend

    restart: always

    env_file:
      - .env

    ports:
      - "8080:8080"

    volumes:
      - ./backend/models:/root/.insightface/models

  nginx:
    image: nginx:alpine

    restart: always

    ports:
      - "80:80"

    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
```

---

# 12. Chạy ứng dụng

## Build

```bash
sudo docker compose build --no-cache
```

## Run

```bash
sudo docker compose up -d
```

---

# 13. Sửa địa chỉ Frontend / Backend

## Backend

Thêm Public IP vào danh sách CORS Origins.

Ví dụ:

```python
origins = [
    "http://<public-ip>"
]
```

## Frontend

Đổi:

```js
localhost
```

thành:

```js
http://<public-ip>:8080
```

---

# 14. Test Camera trên HTTP

Chrome không cho phép truy cập camera qua HTTP.

Trong môi trường test:

```text
chrome://flags
```

Bật:

```text
Insecure origins treated as secure
```

và thêm:

```text
http://<public-ip>
```

---

# 15. CI/CD với GitHub Actions

## Repository Secrets

Setup Secrets: Vào Setting -> Secrets and variables -> Actions -> Tạo 3 New repository secret:

```text
EC2_HOST / <IP Public EC2>
EC2_SSH_KEY / <copy file "my-aws-key.pem">
EC2_USER / ubuntu
```

---

## Workflow

`.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to EC2
        uses: appleboy/ssh-action@v1.0.3

        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}

          script: |
            cd ~/project

            sudo chown -R ubuntu:ubuntu ~/project

            git reset --hard HEAD
            git fetch origin main
            git reset --hard origin/main

            sudo docker compose up -d --build
```

---

# 16. Cấu hình Domain

Có thể sử dụng:

* DuckDNS (miễn phí)

Ví dụ:

```text
attendance-pj.duckdns.org
```

---

# 17. HTTPS với Let's Encrypt

## Dừng ứng dụng

```bash
sudo docker compose down
```

## Cài Certbot

```bash
sudo apt install certbot -y
```

## Xin SSL

```bash
sudo certbot certonly --standalone \
-d <domain>
```

---

# 18. Nginx HTTPS

## Chuyển HTTP → HTTPS

```nginx
server {
    listen 80;
    server_name <domain>;

    return 301 https://$host$request_uri;
}
```

## HTTPS Server

```nginx
server {

    listen 443 ssl;

    server_name <domain>;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;

    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;

    root /usr/share/nginx/html;

    index login.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

# 19. Fix Mixed Content

Khi Frontend chạy HTTPS nhưng Backend chạy HTTP:

```text
Browser sẽ chặn request
```

Giải pháp:

```text
Nginx Reverse Proxy
```

```nginx
location /api/v1/ {

    proxy_pass http://backend:8080/;

    proxy_set_header Host $host;

    proxy_set_header X-Real-IP $remote_addr;

    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

# 20. Full nginx.conf

```nginx
events {}

http {
    include mime.types;

    # Bắt truy cập HTTP (80) và chuyển hướng tự động sang HTTPS (443)
    server {
        listen 80;
        server_name attendance-pj.duckdns.org;
        return 301 https://$host$request_uri;
    }

    # Cấu hình máy chủ HTTPS chính
    server {
        listen 443 ssl;
        server_name attendance-pj.duckdns.org;

        client_max_body_size 10M;

        # Đường dẫn tới chứng chỉ SSL đã lấy từ Let's Encrypt
        ssl_certificate /etc/letsencrypt/live/attendance-pj.duckdns.org/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/attendance-pj.duckdns.org/privkey.pem;

        # Phục vụ Frontend + Đặt login.html làm trang bắt đầu
        location / {
            root /usr/share/nginx/html;
            index login.html;
            try_files $uri $uri/ =404;
        }

        # Lỗi Mixed Content: Khi trang web chạy bằng HTTPS, trình duyệt sẽ chặn đứng mọi kết nối HTTP gửi từ Frontend xuống Backend (port 8080). 
        # Để giải quyết bài toán này, cần cấu hình để Nginx làm "bảo vệ" cho cả Frontend và Backend.
        # Điều hướng API xuống Backend (Fix Mixed Content)
        location /api/v1/ {
            proxy_pass http://backend:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

# 20. Docker Compose HTTPS

```yaml
nginx:
  image: nginx:alpine

  restart: always

  ports:
    - "80:80"
    - "443:443"

  volumes:
    - ./frontend:/usr/share/nginx/html

    - ./nginx.conf:/etc/nginx/nginx.conf:ro

    - /etc/letsencrypt:/etc/letsencrypt:ro
```

---

# 21. Frontend API URL

Không nên dùng:

```js
const API_URL =
"https://example.com/api/v1";
```

Nên dùng:

```js
const API_PREFIX =
"/api/v1";
```

Để nginx tự proxy theo domain hiện tại.

---

# 22. Mở rộng dung lượng EBS

Kiểm tra:

```bash
df -h
lsblk
```

Mở rộng partition:

```bash
sudo growpart /dev/nvme0n1 1
```

Resize filesystem:

```bash
sudo resize2fs /dev/nvme0n1p1
```

Kiểm tra lại:

```bash
df -h /
```

---

# 23. Lỗi Docker Daemon

Lỗi:

```text
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

Kiểm tra:

```bash
sudo systemctl status docker
```

Khởi động:

```bash
sudo systemctl start docker
```

Tự động chạy khi reboot:

```bash
sudo systemctl enable docker
```

Test:

```bash
docker ps
```

---

# 24. Một số lỗi đã gặp

## Sai múi giờ

Triệu chứng:

```text
Không hiển thị dữ liệu chấm công
```

Nguyên nhân:

```text
Server timezone khác Local timezone
```

Khắc phục:

```env
TZ=Asia/Ho_Chi_Minh
```
