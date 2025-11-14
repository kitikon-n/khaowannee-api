from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from decimal import Decimal

from app.db import models
from app.schemas import cryptocurrency as schemas
from app.db.database import get_db

router = APIRouter(
    prefix="/cryptocurrencies",
    tags=["cryptocurrencies"]
)


# =============== GET Endpoint ===============

@router.get("/", response_model=List[schemas.CryptocurrencyResponse])
async def get_all_cryptocurrencies(
    asset_type: Optional[str] = Query(None, description="ประเภทสินทรัพย์ (เช่น CRYPTO, TOKEN, NFT)"),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล cryptocurrencies ทั้งหมด

    - **asset_type**: Filter ตามประเภทสินทรัพย์ (optional)
    - ไม่ต้องใช้ Token (public endpoint)
    - จะคืนค่าเฉพาะ cryptocurrencies ที่ is_active = True
    """
    # Base query
    query = db.query(models.Cryptocurrency).filter(
        models.Cryptocurrency.is_active == True
    )

    # Apply asset_type filter if provided
    if asset_type:
        query = query.filter(models.Cryptocurrency.asset_type == asset_type)

    # Order by name
    cryptocurrencies = query.order_by(models.Cryptocurrency.name).all()

    return cryptocurrencies


@router.get("/{cryptocurrency_id}/price")
async def get_cryptocurrency_price(
    cryptocurrency_id: int,
    db: Session = Depends(get_db)
):
    """
    ดึงราคาล่าสุดของสินทรัพย์

    - **cryptocurrency_id**: ID ของสินทรัพย์
    - ไม่ต้องใช้ Token (public endpoint)
    - คืนค่า close_price ล่าสุดจาก price_data table
    """
    query = text("""
        SELECT
            close_price
        FROM price_data pd
        WHERE pd.cryptocurrency_id = :p_cryptocurrency_id
        ORDER BY pd.price_timestamp DESC
        LIMIT 1
    """)

    result = db.execute(query, {"p_cryptocurrency_id": cryptocurrency_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for cryptocurrency_id {cryptocurrency_id}"
        )

    return {
        "cryptocurrency_id": cryptocurrency_id,
        "close_price": float(row.close_price) if row.close_price else None
    }
