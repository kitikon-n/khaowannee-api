from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

# =============== Portfolio Holding Schemas ===============

class PortfolioHoldingResponse(BaseModel):
    """Schema สำหรับ response ของ portfolio holding"""
    id: int
    portfolio_id: int
    cryptocurrency_id: int
    quantity: Decimal
    average_buy_price: Optional[Decimal] = None
    total_invested: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = None
    profit_loss_percentage: Optional[Decimal] = None
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    created_program: Optional[str] = None
    updated_by: Optional[str] = None
    updated_date: Optional[datetime] = None
    updated_program: Optional[str] = None

    # ข้อมูลเพิ่มเติมจาก JOIN
    portfolio_name: Optional[str] = None
    cryptocurrency_symbol: Optional[str] = None
    cryptocurrency_name: Optional[str] = None

    class Config:
        from_attributes = True
