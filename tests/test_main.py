"""
ตัวอย่างการเขียน Tests สำหรับ FastAPI
ติดตั้ง: pip install pytest pytest-asyncio httpx
รัน: pytest
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.db import models

# สร้าง in-memory SQLite database สำหรับ testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# สร้าง tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# =============== Tests ===============

def test_read_root():
    """ทดสอบ root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI with PostgreSQL"}

def test_health_check():
    """ทดสอบ health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """ทดสอบการสร้าง item"""
    response = client.post(
        "/items",
        json={"title": "Test Item", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "created_at" in data

def test_read_items():
    """ทดสอบการดึงรายการ items"""
    # สร้าง item ก่อน
    client.post(
        "/items",
        json={"title": "Item 1", "description": "Description 1"}
    )
    client.post(
        "/items",
        json={"title": "Item 2", "description": "Description 2"}
    )
    
    # ดึงรายการ items
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_read_item():
    """ทดสอบการดึง item ตาม id"""
    # สร้าง item ก่อน
    create_response = client.post(
        "/items",
        json={"title": "Test Item", "description": "Test Description"}
    )
    item_id = create_response.json()["id"]
    
    # ดึง item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["title"] == "Test Item"

def test_read_item_not_found():
    """ทดสอบการดึง item ที่ไม่มี"""
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_update_item():
    """ทดสอบการอัพเดท item"""
    # สร้าง item ก่อน
    create_response = client.post(
        "/items",
        json={"title": "Original Title", "description": "Original Description"}
    )
    item_id = create_response.json()["id"]
    
    # อัพเดท item
    response = client.put(
        f"/items/{item_id}",
        json={"title": "Updated Title", "description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"

def test_update_item_not_found():
    """ทดสอบการอัพเดท item ที่ไม่มี"""
    response = client.put(
        "/items/99999",
        json={"title": "Title", "description": "Description"}
    )
    assert response.status_code == 404

def test_delete_item():
    """ทดสอบการลบ item"""
    # สร้าง item ก่อน
    create_response = client.post(
        "/items",
        json={"title": "Item to Delete", "description": "Will be deleted"}
    )
    item_id = create_response.json()["id"]
    
    # ลบ item
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
    
    # ตรวจสอบว่า item ถูกลบจริง
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

def test_delete_item_not_found():
    """ทดสอบการลบ item ที่ไม่มี"""
    response = client.delete("/items/99999")
    assert response.status_code == 404

# =============== Parametrized Tests ===============

@pytest.mark.parametrize("title,description", [
    ("Title 1", "Description 1"),
    ("Title 2", "Description 2"),
    ("Title 3", None),  # description เป็น None
])
def test_create_multiple_items(title, description):
    """ทดสอบการสร้าง items หลายแบบ"""
    response = client.post(
        "/items",
        json={"title": title, "description": description}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == title
    assert data["description"] == description

# =============== Async Tests ===============

@pytest.mark.asyncio
async def test_async_create_item():
    """ทดสอบแบบ async"""
    response = client.post(
        "/items",
        json={"title": "Async Item", "description": "Created async"}
    )
    assert response.status_code == 201

# =============== Fixtures ===============

@pytest.fixture
def sample_item():
    """Fixture สำหรับสร้าง sample item"""
    response = client.post(
        "/items",
        json={"title": "Sample Item", "description": "Sample Description"}
    )
    return response.json()

def test_with_fixture(sample_item):
    """ทดสอบโดยใช้ fixture"""
    assert sample_item["title"] == "Sample Item"
    response = client.get(f"/items/{sample_item['id']}")
    assert response.status_code == 200

# =============== Database Tests ===============

def test_database_connection():
    """ทดสอบการเชื่อมต่อ database"""
    db = TestingSessionLocal()
    try:
        # ทดสอบ query พื้นฐาน
        items = db.query(models.Item).all()
        assert isinstance(items, list)
    finally:
        db.close()

# วิธีรัน tests:
# pytest                          # รัน tests ทั้งหมด
# pytest -v                       # แสดง verbose output
# pytest test_main.py             # รัน file เฉพาะ
# pytest -k "test_create"         # รัน tests ที่มี "test_create" ในชื่อ
# pytest --cov=main               # รัน tests พร้อม coverage report
# pytest -x                       # หยุดเมื่อ test fail
# pytest --pdb                    # เปิด debugger เมื่อ test fail
