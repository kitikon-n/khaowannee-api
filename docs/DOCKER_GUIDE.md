# Docker Setup Guide

คู่มือการใช้ Docker สำหรับรัน FastAPI + PostgreSQL

## Prerequisites

- ติดตั้ง Docker และ Docker Compose
- Git (สำหรับ clone โปรเจค)

## การรันด้วย Docker Compose

### 1. สร้างและรัน containers

```bash
# Build และรัน containers ทั้งหมด
docker-compose up -d

# หรือ build ใหม่ทุกครั้ง
docker-compose up -d --build
```

Services ที่จะรัน:
- **FastAPI App**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050

### 2. ตรวจสอบสถานะ containers

```bash
# ดู containers ที่กำลังรัน
docker-compose ps

# ดู logs
docker-compose logs -f

# ดู logs ของ service เดียว
docker-compose logs -f web
```

### 3. เข้าถึง FastAPI

เปิดเบราว์เซอร์:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. เข้าถึง pgAdmin

1. เปิดเบราว์เซอร์ไปที่ http://localhost:5050
2. Login ด้วย:
   - Email: admin@admin.com
   - Password: admin
3. เพิ่ม server ใหม่:
   - Host: db
   - Port: 5432
   - Username: postgres
   - Password: postgres
   - Database: fastapi_db

### 5. หยุดและลบ containers

```bash
# หยุด containers
docker-compose stop

# หยุดและลบ containers
docker-compose down

# หยุด ลบ containers และ volumes (จะลบข้อมูล database)
docker-compose down -v
```

## การรัน Database Migrations

```bash
# เข้าไปใน container
docker-compose exec web bash

# รัน Alembic migrations
alembic upgrade head

# สร้าง migration ใหม่
alembic revision --autogenerate -m "your message"

# ออกจาก container
exit
```

## การทำงานกับ Database โดยตรง

```bash
# เข้าไปใน PostgreSQL container
docker-compose exec db psql -U postgres -d fastapi_db

# หรือจาก host machine (ถ้าติดตั้ง psql)
psql -h localhost -U postgres -d fastapi_db
```

SQL Commands ที่มีประโยชน์:
```sql
-- ดู tables ทั้งหมด
\dt

-- ดูโครงสร้างของ table
\d table_name

-- Query ข้อมูล
SELECT * FROM users;

-- ออกจาก psql
\q
```

## Development Workflow

### การแก้ไขโค้ด

1. แก้ไขไฟล์ในเครื่องของคุณ
2. Docker จะ auto-reload (เพราะมี --reload flag และ mount volume)
3. ตรวจสอบการเปลี่ยนแปลงที่ http://localhost:8000

### การติดตั้ง Python package ใหม่

1. เพิ่ม package ใน `requirements.txt`
2. Rebuild container:
```bash
docker-compose up -d --build
```

### การรัน commands ใน container

```bash
# รัน command แบบครั้งเดียว
docker-compose exec web python script.py

# เปิด shell ใน container
docker-compose exec web bash

# รัน pytest
docker-compose exec web pytest
```

## Troubleshooting

### Port ถูกใช้งานอยู่แล้ว

แก้ไข `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # เปลี่ยนจาก 8000:8000
```

### Database connection error

ตรวจสอบว่า:
1. Database container รันอยู่: `docker-compose ps`
2. Health check ผ่าน: `docker-compose logs db`
3. Environment variables ถูกต้อง

### Container ไม่ start

```bash
# ดู error logs
docker-compose logs

# Rebuild และรันใหม่
docker-compose down
docker-compose up -d --build
```

### ลบ volumes และเริ่มใหม่

```bash
# หยุดและลบทุกอย่าง
docker-compose down -v

# รันใหม่
docker-compose up -d
```

## Production Deployment

สำหรับ production ควรปรับแต่ง:

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    restart: always
    command: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"
    depends_on:
      - db

volumes:
  postgres_data:
```

รัน production:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Useful Commands

```bash
# ดูการใช้ resources
docker stats

# ลบ images ที่ไม่ใช้
docker system prune

# Backup database
docker-compose exec db pg_dump -U postgres fastapi_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres fastapi_db
```

## Best Practices

1. **ใช้ .dockerignore**: สร้างไฟล์เพื่อไม่ copy ไฟล์ที่ไม่จำเป็น
2. **Environment Variables**: ใช้ไฟล์ `.env` สำหรับค่าต่างๆ
3. **Health Checks**: ใช้ health checks สำหรับ services ที่สำคัญ
4. **Volumes**: ใช้ named volumes สำหรับข้อมูลที่ต้องเก็บถาวร
5. **Multi-stage Builds**: ใช้สำหรับ production เพื่อลดขนาด image

## เพิ่มเติม

### ใช้ Redis สำหรับ Caching

เพิ่มใน `docker-compose.yml`:
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

### ใช้ Nginx เป็น Reverse Proxy

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - web
```
