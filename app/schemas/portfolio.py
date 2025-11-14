from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

# =============== Portfolio Schemas ===============

class PortfolioBase(BaseModel):
    """Base schema สำหรับ Portfolio"""
    name: str = Field(..., max_length=100, description="ชื่อ portfolio")
    description: Optional[str] = Field(None, description="รายละเอียด portfolio")
    asset: Optional[str] = Field(None, max_length=10, description="ประเภทสินทรัพย์")
    total_invested: Optional[Decimal] = Field(None, min=0, max=99999999999999999, description="จำนวนเงินที่ลงทุนทั้งหมด")

class PortfolioCreate(PortfolioBase):
    """Schema สำหรับสร้าง portfolio ใหม่"""
    pass


class PortfolioUpdate(BaseModel):
    """Schema สำหรับแก้ไข portfolio (ทุกฟิลด์เป็น optional)"""
    name: Optional[str] = Field(None, max_length=100, description="ชื่อ portfolio")
    description: Optional[str] = Field(None, description="รายละเอียด portfolio")
    asset: Optional[str] = Field(None, max_length=10, description="ประเภทสินทรัพย์")
    total_invested: Optional[Decimal] = Field(None, description="จำนวนเงินที่ลงทุนทั้งหมด")
    current_value: Optional[Decimal] = Field(None, description="มูลค่าปัจจุบัน")
    profit_loss: Optional[Decimal] = Field(None, description="กำไร/ขาดทุน")
    profit_loss_percentage: Optional[Decimal] = Field(None, description="เปอร์เซ็นต์กำไร/ขาดทุน")


class PortfolioResponse(PortfolioBase):
    """Schema สำหรับ response ของ portfolio"""
    id: int
    user_id: int
    total_invested: Optional[Decimal] = 0
    current_value: Optional[Decimal] = 0
    profit_loss: Optional[Decimal] = 0
    profit_loss_percentage: Optional[Decimal] = 0
    asset_name: Optional[str] = None  # ชื่อประเภทสินทรัพย์จาก db_list_value_lang
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    created_program: Optional[str] = None
    updated_by: Optional[str] = None
    updated_date: Optional[datetime] = None
    updated_program: Optional[str] = None

    class Config:
        from_attributes = True


# =============== Nested Data Schemas ===============

class HoldingDetail(BaseModel):
    """Schema สำหรับ holding ใน portfolio detail"""
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
    cryptocurrency_symbol: Optional[str] = None
    cryptocurrency_name: Optional[str] = None
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionDetail(BaseModel):
    """Schema สำหรับ transaction ใน portfolio detail"""
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
    cryptocurrency_symbol: Optional[str] = None
    cryptocurrency_name: Optional[str] = None
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioDetailResponse(BaseModel):
    """Schema สำหรับ portfolio detail พร้อม nested data"""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    total_invested: Optional[Decimal] = 0
    current_value: Optional[Decimal] = 0
    profit_loss: Optional[Decimal] = 0
    profit_loss_percentage: Optional[Decimal] = 0
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    created_program: Optional[str] = None
    updated_by: Optional[str] = None
    updated_date: Optional[datetime] = None
    updated_program: Optional[str] = None
    asset: Optional[str] = None
    asset_name: Optional[str] = None
    portfolio_holdings: List[HoldingDetail] = []
    transactions: List[TransactionDetail] = []
    analysis: List = []  # ยังไม่มีข้อมูล analysis
    overview: List = []  # ยังไม่มีข้อมูล overview

    class Config:
        from_attributes = True
