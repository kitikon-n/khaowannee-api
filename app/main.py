from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from app.db import models
from app.db.database import engine
from app.api import items, suuser, portfolio, portfolio_holding, transaction, cryptocurrency, investment_recommendation
from app.services.binance_price_service import scheduled_price_fetch
from app.services.thai_stock_price_service import scheduled_thai_stock_fetch
from app.services.forex_price_service import scheduled_forex_fetch

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
app.include_router(portfolio.router)
app.include_router(portfolio_holding.router)
app.include_router(transaction.router)
app.include_router(cryptocurrency.router)
app.include_router(investment_recommendation.router)


# =============== APScheduler Setup ===============
# หมายเหตุ: Scheduler ถูกปิดใช้งาน (commented out)
# เปิด comment ด้านล่างถ้าต้องการให้ดึงราคาอัตโนมัติ

# # สร้าง Background Scheduler
# scheduler = BackgroundScheduler()

# from datetime import datetime as dt

# # เพิ่ม job: ดึงราคาจาก Binance ทุก 5 นาที
# scheduler.add_job(
#     func=scheduled_price_fetch,
#     trigger=IntervalTrigger(minutes=5),
#     id="binance_price_fetch",
#     name="Fetch cryptocurrency prices from Binance every 5 minutes",
#     replace_existing=True,
#     next_run_time=dt.now()  # รันทันทีตอน start
# )

# # เพิ่ม job: ดึงราคาหุ้นไทยจาก yfinance ทุก 10 นาที
# scheduler.add_job(
#     func=scheduled_thai_stock_fetch,
#     trigger=IntervalTrigger(minutes=10),
#     id="thai_stock_price_fetch",
#     name="Fetch Thai stock prices from yfinance every 10 minutes",
#     replace_existing=True,
#     next_run_time=dt.now()  # รันทันทีตอน start
# )

# # เพิ่ม job: ดึงอัตราแลกเปลี่ยนจาก ExchangeRate-API ทุก 1 ชั่วโมง
# scheduler.add_job(
#     func=scheduled_forex_fetch,
#     trigger=IntervalTrigger(hours=1),
#     id="forex_price_fetch",
#     name="Fetch forex rates from ExchangeRate-API every 1 hour",
#     replace_existing=True,
#     next_run_time=dt.now()  # รันทันทีตอน start แล้วทุก 1 ชั่วโมง
# )

# # เริ่ม scheduler
# scheduler.start()

# # ปิด scheduler เมื่อ app shutdown
# atexit.register(lambda: scheduler.shutdown())


# =============== Startup Event ===============

@app.on_event("startup")
async def startup_event():
    """เรียกใช้เมื่อ app เริ่มทำงาน"""
    print("=" * 65)
    print("🚀 FastAPI Application Started")
    print("📊 Price Schedulers: DISABLED")
    print("💡 Uncomment scheduler code in main.py to enable")
    print("=" * 65)


@app.on_event("shutdown")
async def shutdown_event():
    """เรียกใช้เมื่อ app หยุดทำงาน"""
    print("=" * 65)
    print("🛑 FastAPI Application Shutting Down")
    print("=" * 65)
