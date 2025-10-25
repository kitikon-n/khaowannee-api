# FastAPI + PostgreSQL Project

โปรเจค FastAPI พื้นฐานที่เชื่อมต่อกับ PostgreSQL

## โครงสร้างโปรเจค

```
.
├── main.py              # ไฟล์หลักของ FastAPI app
├── database.py          # การเชื่อมต่อ database
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example         # ตัวอย่างไฟล์ environment variables
└── README.md           # คู่มือการใช้งาน
```

## การติดตั้ง

### 1. Clone และสร้าง Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า Database

สร้างไฟล์ `.env` จาก `.env.example`:

```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env` ให้ตรงกับ PostgreSQL ของคุณ:

```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. สร้าง Database

```bash
# เข้าไปใน PostgreSQL
psql -U postgres

# สร้าง database
CREATE DATABASE database_name;
```

## การรันโปรเจค

```bash
uvicorn main:app --reload
```

เปิดเบราว์เซอร์ไปที่:
- API: http://localhost:8000
- Swagger UI (เอกสาร API): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### General
- `GET /` - Welcome message
- `GET /health` - Health check

### Items
- `POST /items` - สร้าง item ใหม่
- `GET /items` - ดึงรายการ items (รองรับ pagination)
- `GET /items/{item_id}` - ดึง item ตาม id
- `PUT /items/{item_id}` - อัพเดท item
- `DELETE /items/{item_id}` - ลบ item

## ตัวอย่างการใช้งาน

### สร้าง Item ใหม่

```bash
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Item",
    "description": "This is a test item"
  }'
```

### ดึงรายการ Items

```bash
curl "http://localhost:8000/items"
```

## การพัฒนาต่อ

### เพิ่ม Model ใหม่

1. เพิ่ม class ใหม่ใน `models.py`
2. เพิ่ม schema ใน `schemas.py`
3. เพิ่ม endpoints ใน `main.py`

### การใช้งาน Alembic (Migration)

```bash
# ติดตั้ง Alembic
pip install alembic

# สร้าง migration
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Tips

- ใช้ FastAPI Swagger UI (`/docs`) เพื่อทดสอบ API
- ดู logs ใน terminal เพื่อ debug
- ใช้ `--reload` ใน development เท่านั้น
- ใน production ควรใช้ Gunicorn + Uvicorn workers

## เพิ่ม WebSocket (ถ้าต้องการ)

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

## License

MIT
