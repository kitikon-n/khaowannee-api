"""
Binance Price Service
ดึงราคา cryptocurrency จาก Binance API และบันทึกลง database
"""
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.db import models
from app.db.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinancePriceService:
    """Service สำหรับดึงราคาจาก Binance API"""

    BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
    EXCHANGE_ID = 1  # Hard code exchange_id = 1
    TIMEFRAME = "5M"

    @staticmethod
    def get_cryptocurrencies_to_fetch(db: Session) -> List[Dict]:
        """
        ดึงรายการ cryptocurrencies ที่ต้องการ fetch ราคา
        WHERE asset_type = '02'
        """
        try:
            cryptos = db.query(
                models.Cryptocurrency.id,
                models.Cryptocurrency.symbol
            ).filter(
                models.Cryptocurrency.asset_type == '02',
                models.Cryptocurrency.is_active == True
            ).all()

            return [{"id": crypto.id, "symbol": crypto.symbol} for crypto in cryptos]
        except Exception as e:
            logger.error(f"Error fetching cryptocurrencies: {e}")
            return []

    @staticmethod
    def fetch_binance_price(symbol: str) -> float:
        """
        ดึงราคาจาก Binance API

        Args:
            symbol: เช่น "BTC" จะแปลงเป็น "BTCUSDT"

        Returns:
            float: ราคาปัจจุบัน หรือ None ถ้าเกิด error
        """
        try:
            # แปลง symbol เป็น Binance format (เช่น BTC -> BTCUSDT)
            binance_symbol = f"{symbol}USDT"

            response = requests.get(
                BinancePriceService.BINANCE_API_URL,
                params={"symbol": binance_symbol},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                price = float(data.get("price", 0))
                logger.info(f"Fetched price for {binance_symbol}: {price}")
                return price
            else:
                logger.warning(f"Failed to fetch price for {binance_symbol}: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching Binance price for {symbol}: {e}")
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
                models.PriceData.exchange_id == BinancePriceService.EXCHANGE_ID,
                models.PriceData.timeframe == BinancePriceService.TIMEFRAME
            ).order_by(
                models.PriceData.price_timestamp.desc()
            ).first()

            if existing_price:
                # UPDATE: อัพเดทราคาล่าสุด
                existing_price.close_price = price
                existing_price.price_timestamp = now
                existing_price.updated_by = "scheduler"
                existing_price.updated_date = now
                existing_price.updated_program = "binance_price_service"
                logger.info(f"Updated price for cryptocurrency_id {cryptocurrency_id}: {price}")
            else:
                # INSERT: สร้างข้อมูลใหม่
                new_price = models.PriceData(
                    cryptocurrency_id=cryptocurrency_id,
                    exchange_id=BinancePriceService.EXCHANGE_ID,
                    price_timestamp=now,
                    close_price=price,
                    timeframe=BinancePriceService.TIMEFRAME,
                    created_by="scheduler",
                    created_date=now,
                    created_program="binance_price_service"
                )
                db.add(new_price)
                logger.info(f"Inserted new price for cryptocurrency_id {cryptocurrency_id}: {price}")

            db.commit()

        except Exception as e:
            logger.error(f"Error upserting price data for cryptocurrency_id {cryptocurrency_id}: {e}")
            db.rollback()

    @staticmethod
    def fetch_and_update_all_prices():
        """
        Main function: ดึงราคาทั้งหมดและอัพเดท database
        ใช้สำหรับ scheduler
        """
        logger.info("=== Starting Binance price fetch job ===")
        db = SessionLocal()

        try:
            # 1. ดึงรายการ cryptocurrencies
            cryptos = BinancePriceService.get_cryptocurrencies_to_fetch(db)
            logger.info(f"Found {len(cryptos)} cryptocurrencies to fetch")

            # 2. ดึงราคาจาก Binance และบันทึก
            success_count = 0
            failed_count = 0

            for crypto in cryptos:
                crypto_id = crypto["id"]
                symbol = crypto["symbol"]

                # ดึงราคาจาก Binance
                price = BinancePriceService.fetch_binance_price(symbol)

                if price and price > 0:
                    # บันทึกลง database
                    BinancePriceService.upsert_price_data(db, crypto_id, price)
                    success_count += 1
                else:
                    failed_count += 1

            logger.info(f"=== Binance price fetch completed: {success_count} success, {failed_count} failed ===")

        except Exception as e:
            logger.error(f"Error in fetch_and_update_all_prices: {e}")
        finally:
            db.close()


# Function สำหรับ scheduler เรียกใช้
def scheduled_price_fetch():
    """Function ที่ APScheduler จะเรียกทุก 5 นาที"""
    BinancePriceService.fetch_and_update_all_prices()
