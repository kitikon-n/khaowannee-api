"""
Entry point สำหรับรัน FastAPI application
สามารถรันด้วย: uvicorn main:app --reload
"""
from app.main import app

# Export app เพื่อให้ uvicorn สามารถหาได้
__all__ = ["app"]
