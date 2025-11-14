from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

# =============== Cryptocurrency Schemas ===============

class CryptocurrencyResponse(BaseModel):
    """Schema สำหรับ response ของ cryptocurrency"""
    id: int
    symbol: str
    name: str
    full_name: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    blockchain_network: Optional[str] = None
    launch_date: Optional[date] = None
    is_active: Optional[bool] = True
    asset_type: Optional[str] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    created_program: Optional[str] = None
    updated_by: Optional[str] = None
    updated_date: Optional[datetime] = None
    updated_program: Optional[str] = None

    class Config:
        from_attributes = True
