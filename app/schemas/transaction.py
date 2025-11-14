from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

# =============== Transaction Schemas ===============

class TransactionCreate(BaseModel):
    """Schema สำหรับสร้าง transaction ใหม่"""
    portfolio_id: int = Field(..., description="ID ของ Portfolio")
    cryptocurrency_id: int = Field(..., description="ID ของ Cryptocurrency")
    transaction_type: str = Field(..., description="ประเภท transaction (เช่น BUY, SELL)")
    quantity: Decimal = Field(..., gt=0, description="จำนวน")
    price_per_unit: Decimal = Field(..., gt=0, description="ราคาต่อหน่วย")
    total_amount: Decimal = Field(..., gt=0, description="ยอดรวม")
    fee: Optional[Decimal] = Field(0, ge=0, description="ค่าธรรมเนียม")
    transaction_date: date  = Field(..., description="วันที่ทำธุรกรรม")
    notes: Optional[str] = Field(None, description="หมายเหตุ")


class TransactionUpdate(BaseModel):
    """Schema สำหรับอัพเดท transaction"""
    # cryptocurrency_id: Optional[int] = Field(None, description="ID ของ Cryptocurrency")
    # transaction_type: Optional[str] = Field(None, description="ประเภท transaction")
    quantity: Optional[Decimal] = Field(None, gt=0, description="จำนวน")
    price_per_unit: Optional[Decimal] = Field(None, gt=0, description="ราคาต่อหน่วย")
    total_amount: Optional[Decimal] = Field(None, gt=0, description="ยอดรวม")
    fee: Optional[Decimal] = Field(None, ge=0, description="ค่าธรรมเนียม")
    transaction_date: Optional[date] = Field(None, description="วันที่ทำธุรกรรม")
    notes: Optional[str] = Field(None, description="หมายเหตุ")


class TransactionResponse(BaseModel):
    """Schema สำหรับ response ของ transaction"""
    id: int
    portfolio_id: int
    cryptocurrency_id: int
    transaction_type: str
    quantity: Decimal
    price_per_unit: Decimal
    total_amount: Decimal
    fee: Optional[Decimal] = 0
    transaction_date: datetime
    notes: Optional[str] = None
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
