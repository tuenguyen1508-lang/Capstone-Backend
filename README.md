# Capstone Backend - FastAPI Project

Đây là dự án backend sử dụng **FastAPI**, cơ sở dữ liệu **PostgreSQL** (chạy thông qua Docker), và hệ thống xác thực người dùng bằng **JWT**.

---

## 📌 Các Yêu Cầu Cài Đặt Ban Đầu (Prerequisites)

Để chạy dự án, máy của bạn bắt buộc phải có:
1. **Python 3.8+** trở lên.
2. **Docker** và **Docker Compose**.

### Hướng dẫn cài đặt Docker (Dành cho người chưa cài)
- **Windows / macOS**:
  1. Tải ứng dụng **Docker Desktop** tại: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
  2. Bật file vừa tải về và cài đặt theo hướng dẫn (Next => Install).
  3. Mở ứng dụng Docker Desktop lên và đợi đến khi icon ở góc hiển thị màu xanh (Engine running). Nên tải thêm extention "WSL 2" nếu Windows yêu cầu.
- **Linux**: Làm theo [hướng dẫn cài đặt Docker Engine trên Linux](https://docs.docker.com/engine/install/).

---

## 🏗 Cấu Trúc Dự Án (Folder Structure)

Dự án được thiết kế theo mô hình chuẩn của FastAPI giúp phân tách rõ ràng trách nhiệm của từng thành phần:

\\\	ext
├── app/
│   ├── models/            # 1. Chứa các class SQLAlchemy Model (Ánh xạ các Table trong Database)
│   │   └── user.py        # Định nghĩa bảng Users, Roles và User_Roles
│   ├── routers/           # 2. Chứa các API Endpoint (Tuyến đường), nhận Request và trả Response
│   │   └── auth.py        # API Đăng ký, Đăng nhập, Lấy thông tin user
│   ├── schemas/           # 3. Chứa các Pydantic Model dùng để Validate dữ liệu JSON Request/Response
│   │   └── auth.py        # Format dữ liệu Token, định dạng đầu vào/đầu ra của User
│   ├── services/          # 4. Chứa logic nghiệp vụ phức tạp và bảo mật (Xử lý JWT, Hash Pass, DB Queries)
│   │   └── auth.py        # Logic mã hóa BCrypt, Verify password, Gen Token
│   ├── database.py        # Cấu hình kết nối tới PostgreSQL bằng SQLAlchemy
│   └── main.py            # File Gốc để khởi động toàn bộ ứng dụng FastAPI & gộp Router
├── .env                   # File chứa toàn bộ Biến môi trường (Mật khẩu DB, Secret Keys)
├── .gitignore             # Khai báo các file không muốn đẩy lên Github (.env, venv/, rác...)
├── docker-compose.yml     # Script khởi tạo nhanh CSDL PostgreSQL thông qua Docker Compose
├── requirements.txt       # Danh sách các thư viện Python cần cài đặt
└── README.md              # Tài liệu hướng dẫn sử dụng này
\\\

---

## 🚀 Hướng Dẫn Chạy Dự Án

### Bước 1: Khởi tạo môi trường ảo và cài đặt thư viện
Mở Terminal ở thư mục gốc của dự án (\Capstone-Backend\) và chạy các lệnh sau:

\\\ash
# 1. Tạo môi trường ảo (virtual environment)
python -m venv venv

# 2. Kích hoạt môi trường ảo
# - Hệ điều hành Windows:
.\venv\Scripts\activate
# - Hệ điều hành macOS/Linux:
source venv/bin/activate

# 3. Cài đặt các package bắt buộc từ requirements.txt
pip install -r requirements.txt
\\\

### Bước 2: Cấu hình biến môi trường
Đảm bảo đã có file \.env\ ở thư mục gốc của dự án (cùng cấp với \pp/\) chứa các cấu hình dưới đây (tự tạo nếu chưa có):
\\\env
APP_NAME="Capstone Backend"
APP_ENV=development
PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/capstone
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=capstone

# Authentication
SECRET_KEY=yoursecretkey_please_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
\\\

### Bước 3: Khởi chạy Database bằng Docker Compose
Dự án sử dụng cơ sở dữ liệu PostgreSQL. Bạn chỉ cần chạy lệnh sau để chạy tự động qua Docker:

\\\ash
docker-compose up -d
\\\
*Lưu ý:*
- Khi Terminal in ra chữ "Started" ở container \capstone_db\ nghĩa là thành công.
- Nếu bạn có thay đổi password ở file \.env\, hãy dọn volume cũ trước bằng lệnh: \docker-compose down -v\ và sau đó chạy lại \docker-compose up -d\.

### Bước 4: Khởi chạy ứng dụng FastAPI
Mở kết nối tới server (FastAPI sẽ tự động tạo các bảng \users\, \oles\, và \user_roles\ vào database nhờ hệ thống metadata của SQLAlchemy):

\\\ash
uvicorn app.main:app --reload
\\\

### Bước 5: Cấu hình dữ liệu mẫu cho Roles (Important)
Do hệ thống yêu cầu đăng ký tài khoản (Register) phải khớp với danh sách Role có sẵn (\RESEARCHER\ hoặc \ADMIN\), bạn hãy truy cập trực tiếp vào CSDL Postgres thông qua DBeaver, pgAdmin, DataGrip (User: \postgres\, Pass: \postgres\, Port: \5432\, DB: \capstone\) hoặc trên Terminal và chạy đoạn Script Init Data sau:

\\\sql
INSERT INTO roles (name, code, created_at) VALUES ('Researcher', 'RESEARCHER', NOW());
INSERT INTO roles (name, code, created_at) VALUES ('Administrator', 'ADMIN', NOW());
\\\

---

## 📖 Trải nghiệm API (Tài Liệu Cục Bộ)
Sau khi Server khởi chạy thành công ở Bước 4, mở trình duyệt để tiến hành test API tại:
- **Swagger UI (Dễ dùng, test trực tiếp Auth):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Tiến hành Test luồng chính: \Đăng ký (Register)\ -> \Đăng nhập (Login)\ -> \Lấy thông tin User hiện tại (Get /me)\.
