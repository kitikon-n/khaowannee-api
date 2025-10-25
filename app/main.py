from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import models
from app.db.database import engine
from app.api import items, suuser

# สร้าง tables ทั้งหมดใน database
models.Base.metadata.create_all(bind=engine)

# สร้าง FastAPI app
app = FastAPI(
    title="My FastAPI Project",
    description="FastAPI with PostgreSQL",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในโปรเจคจริงควรระบุ domain ที่อนุญาต
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with PostgreSQL"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(items.router)
app.include_router(suuser.router)
