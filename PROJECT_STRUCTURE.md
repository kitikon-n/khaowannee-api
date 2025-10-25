# โครงสร้างโปรเจกต์

โปรเจกต์ถูกจัดโครงสร้างตามมาตรฐาน FastAPI Best Practices โดยแบ่งหมวดหมู่ดังนี้:

```
project/
├── app/                        # โค้ดหลักของแอปพลิเคชัน
│   ├── __init__.py
│   ├── main.py                # FastAPI application instance และ middleware
│   ├── api/                   # API Routes และ Endpoints
│   │   ├── __init__.py
│   │   └── items.py          # Items endpoints
│   ├── core/                  # Core settings และ configurations
│   │   ├── __init__.py
│   │   └── config.py         # Environment configuration
│   ├── db/                    # Database layer
│   │   ├── __init__.py
│   │   ├── database.py       # Database connection และ session
│   │   └── models.py         # SQLAlchemy models
│   └── schemas/               # Pydantic schemas
│       ├── __init__.py
│       └── item.py           # Item schemas
├── tests/                     # Test files
│   ├── pytest.ini
│   └── test_main.py
├── docs/                      # Documentation
│   ├── README.md
│   ├── QUICK_START.md
│   ├── DOCKER_GUIDE.md
│   ├── ALEMBIC_GUIDE.md
│   └── CLAUDE.md
├── examples/                  # ตัวอย่างโค้ด
│   ├── auth_example.py
│   └── websocket_example.py
├── main.py                    # Entry point สำหรับ uvicorn
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env
└── .gitignore
```

## รายละเอียดโครงสร้าง

### app/ - โค้ดหลักของแอปพลิเคชัน

#### app/main.py
- สร้าง FastAPI application instance
- กำหนด CORS middleware
- Include routers จาก app/api
- Root endpoints (/, /health)

#### app/api/ - API Routes
- **items.py**: CRUD operations สำหรับ items
  - POST /items - สร้าง item ใหม่
  - GET /items - ดึงรายการ items
  - GET /items/{item_id} - ดึง item ตาม id
  - PUT /items/{item_id} - อัพเดท item
  - DELETE /items/{item_id} - ลบ item

#### app/core/ - Core Configuration
- **config.py**: Environment configuration โดยใช้ pydantic-settings
  - DATABASE_URL
  - SECRET_KEY
  - DEBUG

#### app/db/ - Database Layer
- **database.py**:
  - SQLAlchemy engine
  - SessionLocal
  - get_db() dependency
- **models.py**: SQLAlchemy ORM models
  - Item model

#### app/schemas/ - Pydantic Schemas
- **item.py**: Request/Response schemas
  - ItemCreate
  - ItemResponse

### tests/ - Unit Tests
- **test_main.py**: Tests สำหรับ API endpoints
- **pytest.ini**: Pytest configuration

### docs/ - Documentation
- **README.md**: ภาพรวมโปรเจกต์
- **QUICK_START.md**: คู่มือเริ่มต้นใช้งาน 5 นาที
- **DOCKER_GUIDE.md**: คู่มือการใช้งาน Docker
- **ALEMBIC_GUIDE.md**: คู่มือ Database Migration
- **CLAUDE.md**: คำแนะนำสำหรับ Claude Code

### examples/ - ตัวอย่างโค้ด
- **auth_example.py**: ตัวอย่างการทำ Authentication
- **websocket_example.py**: ตัวอย่างการใช้ WebSocket

### main.py - Entry Point
- Import app จาก app.main
- ใช้สำหรับรัน uvicorn: `uvicorn main:app --reload`

## วิธีการใช้งาน

### รัน Application

```bash
# Local development
uvicorn main:app --reload

# หรือระบุ port
uvicorn main:app --reload --port 8001

# Docker
docker-compose up -d
```

### รัน Tests

```bash
# รัน tests ทั้งหมด
pytest

# รัน tests ใน file เฉพาะ
pytest tests/test_main.py

# รัน tests พร้อม coverage
pytest --cov=app --cov-report=html
```

### เพิ่ม API Endpoint ใหม่

1. สร้างไฟล์ใน `app/api/` เช่น `users.py`
2. สร้าง schemas ใน `app/schemas/` เช่น `user.py`
3. สร้าง model ใน `app/db/models.py` (ถ้าต้องการ)
4. Include router ใน `app/main.py`:
   ```python
   from app.api import items, users
   app.include_router(users.router)
   ```

### เพิ่ม Database Model ใหม่

1. เพิ่ม model ใน `app/db/models.py`
2. สร้าง Pydantic schema ใน `app/schemas/`
3. สร้าง Alembic migration:
   ```bash
   alembic revision --autogenerate -m "Add new model"
   alembic upgrade head
   ```

## ข้อดีของโครงสร้างนี้

1. **แยกหมวดหมู่ชัดเจน**: แต่ละส่วนมีหน้าที่เฉพาะ
2. **ง่ายต่อการขยาย**: เพิ่ม features ใหม่ได้ง่าย
3. **ทดสอบง่าย**: แยก logic ออกจาก routes
4. **มาตรฐาน**: ตาม FastAPI Best Practices
5. **บำรุงรักษาง่าย**: โค้ดเป็นระเบียบ หาง่าย

## การ Import

เนื่องจากโครงสร้างใหม่ การ import จะเป็นแบบนี้:

```python
# Import models
from app.db import models

# Import schemas
from app.schemas import item as item_schemas

# Import database
from app.db.database import get_db

# Import config
from app.core.config import settings
```
