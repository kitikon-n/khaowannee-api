"""
Forex Price Service
ดึงอัตราแลกเปลี่ยนจาก ExchangeRate-API และบันทึกลง database
"""
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Optional
import logging

from app.db import models
from app.db.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForexPriceService:
    """Service สำหรับดึงอัตราแลกเปลี่ยนจาก ExchangeRate-API"""

    # ExchangeRate-API (Free, ไม่ต้องใช้ API key)
    # Documentation: https://www.exchangerate-api.com/docs/overview
    EXCHANGERATE_API_URL = "https://api.exchangerate-api.com/v4/latest"

    EXCHANGE_ID = 3  # Hard code exchange_id = 3 สำหรับ Forex
    TIMEFRAME = "1H"

    @staticmethod
    def get_forex_to_fetch(db: Session) -> List[Dict]:
        """
        ดึงรายการสกุลเงินที่ต้องการ fetch อัตราแลกเปลี่ยน
        WHERE asset_type = '01' AND is_active = true
        """
        try:
            query = text("""
                SELECT
                    c.id,
                    c.symbol AS value,
                    c.name AS text,
                    c.base_currency,
                    c.quote_currency
                FROM cryptocurrencies c
                WHERE c.asset_type = :asset_type
                AND c.is_active IS true
            """)

            result = db.execute(query, {"asset_type": "01"})
            rows = result.fetchall()

            return [
                {
                    "id": row.id,
                    "symbol": row.value,
                    "name": row.text,
                    "base_currency": row.base_currency,
                    "quote_currency": row.quote_currency
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error fetching forex list: {e}")
            return []

    @staticmethod
    def fetch_forex_rate(base_currency: str, quote_currency: str) -> Optional[float]:
        """
        ดึงอัตราแลกเปลี่ยนจาก ExchangeRate-API

        Args:
            base_currency: สกุลเงินต้นทาง (เช่น EUR, GBP)
            quote_currency: สกุลเงินปลายทาง (เช่น USD, JPY)

        Returns:
            float: อัตราแลกเปลี่ยน หรือ None ถ้า error

        ExchangeRate-API Response Format:
        {
            "base": "EUR",
            "date": "2025-11-03",
            "rates": {
                "USD": 1.0856,
                "JPY": 165.82,
                "GBP": 0.8342,
                ...
            }
        }
        """
        try:
            # ถ้าเป็นสกุลเดียวกัน
            if base_currency.upper() == quote_currency.upper():
                return 1.0

            # เรียก API: /v4/latest/{base_currency}
            url = f"{ForexPriceService.EXCHANGERATE_API_URL}/{base_currency.upper()}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # ดึง rates จาก response
                rates = data.get("rates", {})

                # หา quote_currency rate
                rate = rates.get(quote_currency.upper())

                if rate:
                    logger.info(f"Exchange rate {base_currency}/{quote_currency}: {rate}")
                    return float(rate)
                else:
                    logger.warning(f"No rate found for {quote_currency} in {base_currency} rates")
                    return None
            else:
                logger.warning(f"Failed to fetch rate for {base_currency}: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching forex rate for {base_currency}/{quote_currency}: {e}")
            return None

    @staticmethod
    def upsert_price_data(db: Session, cryptocurrency_id: int, rate: float):
        """
        เพิ่มหรืออัพเดทอัตราแลกเปลี่ยนใน price_data table
        - ถ้าไม่มีข้อมูล -> INSERT
        - ถ้ามีข้อมูล -> UPDATE
        """
        try:
            now = datetime.now()

            # ค้นหาข้อมูลล่าสุดของ cryptocurrency_id นี้
            existing_price = db.query(models.PriceData).filter(
                models.PriceData.cryptocurrency_id == cryptocurrency_id,
                models.PriceData.exchange_id == ForexPriceService.EXCHANGE_ID,
                models.PriceData.timeframe == ForexPriceService.TIMEFRAME
            ).order_by(
                models.PriceData.price_timestamp.desc()
            ).first()

            if existing_price:
                # UPDATE: อัพเดทอัตราแลกเปลี่ยนล่าสุด
                existing_price.close_price = rate
                existing_price.price_timestamp = now
                existing_price.updated_by = "scheduler"
                existing_price.updated_date = now
                existing_price.updated_program = "forex_price_service"
                logger.info(f"Updated Forex rate for cryptocurrency_id {cryptocurrency_id}: {rate}")
            else:
                # INSERT: สร้างข้อมูลใหม่
                new_price = models.PriceData(
                    cryptocurrency_id=cryptocurrency_id,
                    exchange_id=ForexPriceService.EXCHANGE_ID,
                    price_timestamp=now,
                    close_price=rate,
                    timeframe=ForexPriceService.TIMEFRAME,
                    created_by="scheduler",
                    created_date=now,
                    created_program="forex_price_service"
                )
                db.add(new_price)
                logger.info(f"Inserted new Forex rate for cryptocurrency_id {cryptocurrency_id}: {rate}")

            db.commit()

        except Exception as e:
            logger.error(f"Error upserting price data for cryptocurrency_id {cryptocurrency_id}: {e}")
            db.rollback()

    @staticmethod
    def fetch_and_update_all_prices():
        """
        Main function: ดึงอัตราแลกเปลี่ยนทั้งหมดและอัพเดท database
        ใช้สำหรับ scheduler
        """
        logger.info("=== Starting Forex price fetch job (ExchangeRate-API) ===")
        db = SessionLocal()

        try:
            # 1. ดึงรายการสกุลเงิน
            forex_list = ForexPriceService.get_forex_to_fetch(db)
            logger.info(f"Found {len(forex_list)} forex currencies to fetch")

            if not forex_list:
                logger.warning("No forex currencies found in database")
                return

            # 2. ดึงอัตราแลกเปลี่ยนแต่ละสกุลเงินจาก ExchangeRate-API
            # หมายเหตุ: ExchangeRate-API free tier: 1,500 requests/month (50 requests/day)
            success_count = 0
            failed_count = 0

            for forex in forex_list:
                forex_id = forex["id"]
                base_currency = forex["base_currency"]
                quote_currency = forex["quote_currency"]

                # ดึงอัตราแลกเปลี่ยน (รองรับทั้ง direct และ cross pairs)
                rate = ForexPriceService.fetch_forex_rate(base_currency, quote_currency)

                if rate and rate > 0:
                    # บันทึกลง database
                    ForexPriceService.upsert_price_data(db, forex_id, rate)
                    success_count += 1
                else:
                    failed_count += 1

            logger.info(f"=== Forex price fetch completed: {success_count} success, {failed_count} failed ===")

        except Exception as e:
            logger.error(f"Error in fetch_and_update_all_prices: {e}")
        finally:
            db.close()


# Function สำหรับ scheduler เรียกใช้
def scheduled_forex_fetch():
    """Function ที่ APScheduler จะเรียกทุก 1 ชั่วโมง"""
    ForexPriceService.fetch_and_update_all_prices()
