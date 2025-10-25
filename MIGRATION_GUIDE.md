# Migration Guide: แก้ไข Password Column

## ปัญหา
bcrypt hash password ต้องการ **60-80 characters** แต่ `su_user.password` มีแค่ **VARCHAR(50)**

## วิธีแก้ไข

### วิธีที่ 1: รัน SQL โดยตรง (เร็วที่สุด)

```bash
# เข้า PostgreSQL
psql -U postgres -d your_database_name

# รัน SQL
ALTER TABLE su_user ALTER COLUMN password TYPE VARCHAR(200);

# ตรวจสอบ
\d su_user
```

หรือใช้ไฟล์ SQL:
```bash
psql -U postgres -d your_database_name -f fix_password_column.sql
```

### วิธีที่ 2: ใช้ Alembic (แนะนำสำหรับ Production)

#### 1. ติดตั้ง Alembic
```bash
pip install alembic
```

#### 2. สร้าง Alembic environment
```bash
alembic init alembic
```

#### 3. แก้ไข `alembic.ini`
```ini
sqlalchemy.url = postgresql://user:password@localhost/dbname
```

#### 4. แก้ไข `alembic/env.py`
```python
from app.db.database import Base
from app.db.models import *  # Import all models

target_metadata = Base.metadata
```

#### 5. สร้าง Migration
```bash
alembic revision -m "Increase password column length to 200"
```

#### 6. แก้ไขไฟล์ migration ที่สร้าง
```python
def upgrade():
    op.alter_column('su_user', 'password',
                    existing_type=sa.VARCHAR(length=50),
                    type_=sa.VARCHAR(length=200),
                    existing_nullable=True)

def downgrade():
    op.alter_column('su_user', 'password',
                    existing_type=sa.VARCHAR(length=200),
                    type_=sa.VARCHAR(length=50),
                    existing_nullable=True)
```

#### 7. รัน Migration
```bash
alembic upgrade head
```

### วิธีที่ 3: ใช้ pgAdmin (GUI)

1. เปิด pgAdmin
2. เลือก database → Tables → su_user
3. คลิกขวา → Properties → Columns
4. เลือก `password` column
5. เปลี่ยน Length จาก 50 → 200
6. กด Save

## ตรวจสอบว่าแก้ไขสำเร็จ

```sql
SELECT
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'su_user'
AND column_name = 'password';
```

ควรได้:
```
column_name | data_type         | character_maximum_length
------------+-------------------+------------------------
password    | character varying | 200
```

## ข้อมูลเพิ่มเติม

### ขนาด Password ที่แนะนำ:

| Algorithm | Minimum Length | Recommended |
|-----------|---------------|-------------|
| bcrypt    | 60            | 80-100      |
| argon2    | 95            | 100         |
| pbkdf2    | 88            | 100         |

### bcrypt hash format:
```
$2b$12$KIXxP5QY7Z8N9X1Y2Z3A4u5B6C7D8E9F0G1H2I3J4K5L6M7N8O9P0
│││ │├────────────────┬────────────────────────────────┤
│││ ││               └─ hash (31 chars)
│││ │└─ salt (22 chars)
│││ └─ cost factor (2 chars)
││└─ minor revision
│└─ bcrypt identifier
└─ $ delimiter

Total: 60 characters
```

## หลังแก้ไขแล้ว

ลองสมัครสมาชิกใหม่:

```bash
POST /user/register
{
  "user_name": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

Password จะถูก hash เป็น:
```
$2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNO
```
(60 ตัวอักษร - พอดีกับ VARCHAR(200))
