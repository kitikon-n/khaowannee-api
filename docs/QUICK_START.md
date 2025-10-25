# 🚀 Quick Start Guide

เริ่มต้นใช้งาน FastAPI + PostgreSQL ภายใน 5 นาที!

## ⚡ วิธีที่ 1: รันแบบปกติ (Recommended สำหรับ Development)

### ขั้นตอนที่ 1: ติดตั้ง Dependencies

```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน virtual environment
# บน macOS/Linux:
source venv/bin/activate
# บน Windows:
venv\Scripts\activate

# ติดตั้ง packages
pip install -r requirements.txt
```

### ขั้นตอนที่ 2: ตั้งค่า Database

```bash
# สร้างไฟล์ .env
cp .env.example .env

# แก้ไข .env ให้ตรงกับ PostgreSQL ของคุณ
# DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### ขั้นตอนที่ 3: สร้าง Database

```bash
# เข้าไปใน PostgreSQL
psql -U postgres

# สร้าง database
CREATE DATABASE fastapi_db;
\q
```

### ขั้นตอนที่ 4: รัน Application

```bash
uvicorn main:app --reload
```

✅ เสร็จแล้ว! เปิดเบราว์เซอร์ไปที่:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Endpoint**: http://localhost:8000

---

## 🐳 วิธีที่ 2: รันด้วย Docker (Recommended สำหรับ Production)

### เพียง 2 คำสั่ง!

```bash
# 1. Build และรัน containers
docker-compose up -d

# 2. เปิดเบราว์เซอร์
```

✅ เสร็จแล้ว! เข้าใช้งานได้ที่:
- **FastAPI**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@admin.com / admin)

---

## 📝 ทดสอบ API

### 1. สร้าง Item

```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Item",
    "description": "This is awesome!"
  }'
```

### 2. ดึงรายการ Items

```bash
curl "http://localhost:8000/items"
```

### 3. ดึง Item ตาม ID

```bash
curl "http://localhost:8000/items/1"
```

---

## 🎯 ขั้นตอนถัดไป

### เพิ่ม Authentication

```bash
# ดูตัวอย่างใน auth_example.py
uvicorn auth_example:app --reload
```

### เพิ่ม WebSocket

```bash
# ดูตัวอย่างใน websocket_example.py
uvicorn websocket_example:app --reload
```

### ใช้ Database Migrations

```bash
# ติดตั้ง Alembic
pip install alembic

# อ่านคู่มือที่ ALEMBIC_GUIDE.md
```

### รัน Tests

```bash
# ติดตั้ง pytest
pip install pytest pytest-asyncio httpx

# รัน tests
pytest
```

---

## 📚 เอกสารเพิ่มเติม

- **README.md** - คู่มือหลักและโครงสร้างโปรเจค
- **ALEMBIC_GUIDE.md** - การใช้งาน Database Migrations
- **DOCKER_GUIDE.md** - คู่มือ Docker แบบละเอียด
- **auth_example.py** - ตัวอย่างการทำ Authentication
- **websocket_example.py** - ตัวอย่างการใช้ WebSocket
- **test_main.py** - ตัวอย่างการเขียน Unit Tests

---

## 🛠️ Troubleshooting

### Port 8000 ถูกใช้งานอยู่

```bash
# เปลี่ยน port เป็น 8001
uvicorn main:app --reload --port 8001
```

### Database Connection Error

ตรวจสอบ:
1. PostgreSQL รันอยู่หรือไม่
2. DATABASE_URL ในไฟล์ `.env` ถูกต้องหรือไม่
3. Database ถูกสร้างแล้วหรือยัง

### Import Error

```bash
# ตรวจสอบว่า virtual environment เปิดอยู่
which python

# ควรแสดง path ของ virtual environment
# ถ้าไม่ใช่ ให้ activate ใหม่
source venv/bin/activate
```

---

## 💡 Tips

1. **ใช้ Swagger UI** (`/docs`) เพื่อทดสอบ API อย่างง่ายดาย
2. **Auto-reload** จะทำงานเมื่อบันทึกไฟล์ (ใช้ `--reload` flag)
3. **ดู logs** ใน terminal เพื่อ debug
4. **ใช้ pgAdmin** เพื่อจัดการ database ผ่าน GUI

---

## 🎓 Learning Path

1. ✅ เริ่มต้นด้วย Quick Start นี้
2. 📖 อ่าน README.md เพื่อเข้าใจโครงสร้าง
3. 🔐 ลองเพิ่ม Authentication (auth_example.py)
4. 🔄 ทำความเข้าใจ Database Migrations (ALEMBIC_GUIDE.md)
5. 🧪 เขียน Tests (test_main.py)
6. 🐳 Deploy ด้วย Docker (DOCKER_GUIDE.md)

---

## 📞 Need Help?

- อ่านเอกสารใน `/docs` ของโปรเจค
- ตรวจสอบ error logs ใน terminal
- ดู Swagger UI เพื่อทดสอบ API

Happy Coding! 🎉
