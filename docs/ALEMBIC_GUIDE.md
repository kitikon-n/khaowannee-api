# Database Migrations ด้วย Alembic

## การติดตั้งและตั้งค่า Alembic

### 1. ติดตั้ง Alembic

```bash
pip install alembic
```

### 2. Initial Setup

```bash
# สร้างโฟลเดอร์ alembic และไฟล์ config
alembic init alembic
```

### 3. แก้ไขไฟล์ alembic.ini

เปลี่ยน:
```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

เป็น:
```ini
# ลบบรรทัดนี้ออก หรือคอมเมนต์
# sqlalchemy.url = 
```

### 4. แก้ไขไฟล์ alembic/env.py

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# เพิ่ม imports
from config import settings
from database import Base
import models  # import models เพื่อให้ Alembic รู้จัก

# ตั้งค่า target_metadata
target_metadata = Base.metadata

# ใน run_migrations_offline() และ run_migrations_online()
# แก้ไข config ให้ใช้ database_url จาก settings

def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

## การใช้งาน Alembic

### สร้าง Migration แรก

```bash
# สร้าง migration file อัตโนมัติจาก models
alembic revision --autogenerate -m "Initial migration"
```

### รัน Migration

```bash
# รัน migrations ทั้งหมด
alembic upgrade head

# รัน migration ล่าสุด
alembic upgrade +1

# Downgrade 1 version
alembic downgrade -1

# กลับไปยัง base (ลบทุกอย่าง)
alembic downgrade base
```

### ตรวจสอบ Migration History

```bash
# ดู current version
alembic current

# ดู history
alembic history

# ดู history พร้อม verbose
alembic history --verbose
```

### สร้าง Migration แบบ Manual

```bash
alembic revision -m "add user role column"
```

จากนั้นแก้ไขไฟล์ที่สร้างขึ้นใน `alembic/versions/`:

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'role')
```

## ตัวอย่างการเพิ่ม Column

```bash
# สมมติเพิ่ม column ใน models.py
# class User(Base):
#     ...
#     role = Column(String, default="user")

# สร้าง migration
alembic revision --autogenerate -m "add role to users"

# รัน migration
alembic upgrade head
```

## ตัวอย่างการสร้าง Table ใหม่

```bash
# เพิ่ม model ใหม่ใน models.py
# class Post(Base):
#     __tablename__ = "posts"
#     id = Column(Integer, primary_key=True)
#     title = Column(String)
#     content = Column(Text)

# สร้าง migration
alembic revision --autogenerate -m "add posts table"

# รัน migration
alembic upgrade head
```

## Tips

1. **ตรวจสอบ Migration ก่อนรัน**: เปิดไฟล์ migration ใน `alembic/versions/` และตรวจสอบก่อนรัน
2. **Backup Database**: สำรอง database ก่อนรัน migration ใน production
3. **Test ใน Development ก่อน**: ทดสอบ migration ใน dev environment ก่อน
4. **ใช้ Descriptive Messages**: ใช้ชื่อที่บอกความหมายชัดเจนใน migration message
5. **Commit Migration Files**: เก็บไฟล์ migration ใน git repository

## Troubleshooting

### Migration ไม่ detect การเปลี่ยนแปลง
- ตรวจสอบว่า import models ใน `alembic/env.py` แล้ว
- ตรวจสอบว่า `target_metadata = Base.metadata` ถูกต้อง

### Error เกี่ยวกับ Database URL
- ตรวจสอบว่าแก้ไข `alembic/env.py` ให้ใช้ `settings.database_url` แล้ว

### Table หรือ Column มีอยู่แล้ว
```bash
# Stamp current state without running
alembic stamp head
```

## Structure ของ Migration File

```python
"""add user role

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # คำสั่งสำหรับ upgrade
    pass

def downgrade() -> None:
    # คำสั่งสำหรับ downgrade (ย้อนกลับ)
    pass
```
