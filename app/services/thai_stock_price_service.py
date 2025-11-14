"""
Thai Stock Price Service
ดึงราคาหุ้นไทยจาก Yahoo Finance (yfinance) และบันทึกลง database
"""
from __future__ import annotations
import yfinance as yf
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.db import models
from app.db.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThaiStockPriceService:
    """Service สำหรับดึงราคาหุ้นไทยจาก yfinance"""

    EXCHANGE_ID = 2  # Hard code exchange_id = 2 สำหรับหุ้นไทย
    TIMEFRAME = "10M"

    @staticmethod
    def get_stocks_to_fetch(db: Session) -> List[Dict]:
        """
        ดึงรายการหุ้นไทยที่ต้องการ fetch ราคา
        WHERE asset_type = '03'
        """
        try:
            stocks = db.query(
                models.Cryptocurrency.id,
                models.Cryptocurrency.symbol
            ).filter(
                models.Cryptocurrency.asset_type == '03',
                models.Cryptocurrency.is_active == True
            ).all()

            return [{"id": stock.id, "symbol": stock.symbol} for stock in stocks]
        except Exception as e:
            logger.error(f"Error fetching Thai stocks: {e}")
            return []

    @staticmethod
    def fetch_thai_stock_price(symbol: str) -> float:
        """
        ดึงราคาหุ้นไทยจาก Yahoo Finance (yfinance)

        Args:
            symbol: เช่น "PTT" จะแปลงเป็น "PTT.BK" (Bangkok Stock Exchange)

        Returns:
            float: ราคาปัจจุบัน หรือ None ถ้าเกิด error
        """
        try:
            # แปลง symbol เป็น Yahoo Finance format สำหรับตลาดหุ้นไทย
            yf_symbol = f"{symbol}.BK"

            # ดึงข้อมูลหุ้น
            ticker = yf.Ticker(yf_symbol)

            # ดึงราคาปัจจุบัน (fast_info.last_price หรือ info['regularMarketPrice'])
            try:
                # วิธีที่ 1: ใช้ fast_info (เร็วกว่า)
                price = ticker.fast_info.get('lastPrice')
                if price is None or price == 0:
                    # วิธีที่ 2: ใช้ history (ช้ากว่าแต่น่าเชื่อถือ)
                    hist = ticker.history(period='1d')
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                    else:
                        price = None
            except Exception:
                # Fallback: ใช้ history
                hist = ticker.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                else:
                    price = None

            if price and price > 0:
                logger.info(f"Fetched price for {yf_symbol}: {price}")
                return float(price)
            else:
                logger.warning(f"No valid price data for {yf_symbol}")
                return None

        except Exception as e:
            logger.error(f"Error fetching Thai stock price for {symbol}: {e}")
            return None

    @staticmethod
    def upsert_price_data(db: Session, cryptocurrency_id: int, price: float):
        """
        เพิ่มหรืออัพเดทราคาใน price_data table
        - ถ้าไม่มีข้อมูล -> INSERT
        - ถ้ามีข้อมูล -> UPDATE
        """
        try:
            now = datetime.now()

            # ค้นหาข้อมูลล่าสุดของ cryptocurrency_id นี้
            existing_price = db.query(models.PriceData).filter(
                models.PriceData.cryptocurrency_id == cryptocurrency_id,
                models.PriceData.exchange_id == ThaiStockPriceService.EXCHANGE_ID,
                models.PriceData.timeframe == ThaiStockPriceService.TIMEFRAME
            ).order_by(
                models.PriceData.price_timestamp.desc()
            ).first()

            if existing_price:
                # UPDATE: อัพเดทราคาล่าสุด
                existing_price.close_price = price
                existing_price.price_timestamp = now
                existing_price.updated_by = "scheduler"
                existing_price.updated_date = now
                existing_price.updated_program = "thai_stock_price_service"
                logger.info(f"Updated Thai stock price for cryptocurrency_id {cryptocurrency_id}: {price}")
            else:
                # INSERT: สร้างข้อมูลใหม่
                new_price = models.PriceData(
                    cryptocurrency_id=cryptocurrency_id,
                    exchange_id=ThaiStockPriceService.EXCHANGE_ID,
                    price_timestamp=now,
                    close_price=price,
                    timeframe=ThaiStockPriceService.TIMEFRAME,
                    created_by="scheduler",
                    created_date=now,
                    created_program="thai_stock_price_service"
                )
                db.add(new_price)
                logger.info(f"Inserted new Thai stock price for cryptocurrency_id {cryptocurrency_id}: {price}")

            db.commit()

        except Exception as e:
            logger.error(f"Error upserting price data for cryptocurrency_id {cryptocurrency_id}: {e}")
            db.rollback()

    @staticmethod
    def fetch_and_update_all_prices():
        """
        Main function: ดึงราคาหุ้นไทยทั้งหมดและอัพเดท database
        ใช้สำหรับ scheduler
        """
        logger.info("=== Starting Thai Stock price fetch job ===")
        db = SessionLocal()

        try:
            # 1. ดึงรายการหุ้นไทย
            stocks = ThaiStockPriceService.get_stocks_to_fetch(db)
            logger.info(f"Found {len(stocks)} Thai stocks to fetch")

            # 2. ดึงราคาจาก yfinance และบันทึก
            success_count = 0
            failed_count = 0

            for stock in stocks:
                stock_id = stock["id"]
                symbol = stock["symbol"]

                # ดึงราคาจาก yfinance
                price = ThaiStockPriceService.fetch_thai_stock_price(symbol)

                if price and price > 0:
                    # บันทึกลง database
                    ThaiStockPriceService.upsert_price_data(db, stock_id, price)
                    success_count += 1
                else:
                    failed_count += 1

            logger.info(f"=== Thai Stock price fetch completed: {success_count} success, {failed_count} failed ===")

        except Exception as e:
            logger.error(f"Error in fetch_and_update_all_prices: {e}")
        finally:
            db.close()


# Function สำหรับ scheduler เรียกใช้
def scheduled_thai_stock_fetch():
    """Function ที่ APScheduler จะเรียกทุก 10 นาที"""
    ThaiStockPriceService.fetch_and_update_all_prices()
