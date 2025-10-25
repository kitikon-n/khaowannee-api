from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# สร้าง database engine พร้อม connection pool settings
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,          # ตรวจสอบ connection ก่อนใช้งาน
    pool_recycle=3600,            # Recycle connection ทุก 1 ชั่วโมง
    pool_size=5,                  # Connection pool size
    max_overflow=10,              # Max overflow connections
    connect_args={
        "connect_timeout": 10,    # Connection timeout 10 วินาที
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

# สร้าง SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# สร้าง Base class สำหรับ models
Base = declarative_base()

# Dependency สำหรับ get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
