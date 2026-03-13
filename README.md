# Capstone Backend - FastAPI Project

Backend service được xây dựng bằng **FastAPI**, sử dụng **PostgreSQL**
làm cơ sở dữ liệu (chạy qua Docker) và **JWT Authentication** để xác
thực người dùng.

------------------------------------------------------------------------

# 📌 Prerequisites

Để chạy dự án, máy của bạn cần cài đặt:

-   **Python 3.8+**
-   **Docker**
-   **Docker Compose**

------------------------------------------------------------------------

# 🐳 Cài đặt Docker (Nếu chưa có)

### Windows / macOS

1.  Tải **Docker Desktop**\
    https://www.docker.com/products/docker-desktop/

2.  Cài đặt theo hướng dẫn.

3.  Mở **Docker Desktop** và chờ trạng thái:

```{=html}
<!-- -->
```
    Engine Running

4.  Nếu Windows yêu cầu, hãy cài **WSL2**.

------------------------------------------------------------------------

### Linux

Làm theo hướng dẫn chính thức:

https://docs.docker.com/engine/install/

------------------------------------------------------------------------

# 🏗 Project Structure

Dự án được tổ chức theo kiến trúc chuẩn của **FastAPI**.

    Capstone-Backend
    │
    ├── app/
    │   ├── models/        # SQLAlchemy Models (Database Tables)
    │   │   └── user.py
    │   │
    │   ├── routers/       # API Endpoints
    │   │   └── auth.py
    │   │
    │   ├── schemas/       # Pydantic Schemas (Request / Response validation)
    │   │   └── auth.py
    │   │
    │   ├── services/      # Business logic & Security
    │   │   └── auth.py
    │   │
    │   ├── database.py    # Database connection config
    │   └── main.py        # FastAPI entry point
    │
    ├── .env               # Environment variables
    ├── .gitignore
    ├── docker-compose.yml # PostgreSQL container
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

# 🚀 Run Project

## 1️⃣ Tạo Virtual Environment

Mở terminal tại thư mục project.

``` bash
python -m venv venv
```

------------------------------------------------------------------------

## 2️⃣ Kích hoạt môi trường ảo

### Windows

``` bash
.\venv\Scripts\activate
```

### macOS / Linux

``` bash
source venv/bin/activate
```

------------------------------------------------------------------------

## 3️⃣ Cài đặt dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# ⚙️ Environment Variables

Tạo file `.env` ở root project:

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

------------------------------------------------------------------------

# 🐘 Start PostgreSQL (Docker)

Chạy database bằng Docker:

``` bash
docker-compose up -d
```

Nếu bạn thay đổi password trong `.env`, hãy reset volume:

``` bash
docker-compose down -v
docker-compose up -d
```

Khi container **capstone_db** hiển thị `Started` nghĩa là database đã
chạy thành công.

------------------------------------------------------------------------

# ▶️ Start FastAPI Server

Chạy server:

``` bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại:

    http://127.0.0.1:8000

FastAPI sẽ tự động tạo các bảng:

-   users
-   roles
-   user_roles

------------------------------------------------------------------------

# 🗄 Init Role Data (Important)

Hệ thống yêu cầu **Role phải tồn tại trước khi đăng ký user**.

Kết nối vào PostgreSQL bằng:

-   **pgAdmin**
-   **DBeaver**
-   **DataGrip**

Thông tin kết nối:

    Host: localhost
    Port: 5432
    Database: capstone
    User: postgres
    Password: postgres

Sau đó chạy SQL:

``` sql
INSERT INTO roles (name, code, created_at)
VALUES ('Researcher', 'RESEARCHER', NOW());

INSERT INTO roles (name, code, created_at)
VALUES ('Administrator', 'ADMIN', NOW());
```

------------------------------------------------------------------------

# 📖 API Documentation

Sau khi server chạy, truy cập:

### Swagger UI

http://127.0.0.1:8000/docs

### ReDoc

http://127.0.0.1:8000/redoc

------------------------------------------------------------------------

# 🔑 Test Flow

Bạn có thể test API theo flow:

    Register
       ↓
    Login
       ↓
    Get Current User (/me)

------------------------------------------------------------------------

# 🧑‍💻 Tech Stack

-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Docker
-   JWT Authentication
-   Pydantic
