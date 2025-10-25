from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# =============== Token Schemas ===============

class Token(BaseModel):
    """Schema สำหรับ Token Response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema สำหรับข้อมูลใน Token"""
    username: Optional[str] = None
    user_id: Optional[int] = None


# =============== Login Schemas ===============
class Login(BaseModel):
    """Schema สำหรับ login (username + password)"""
    username: str = Field(..., min_length=3, max_length=20, description="Username")
    password: str = Field(..., min_length=6, description="Password")


# User Registration Schema
class UserCreate(BaseModel):
    """Schema สำหรับสร้าง user ใหม่"""
    user_name: str = Field(..., min_length=3, max_length=20, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (will be hashed)")


# User Response Schema
class UserResponse(BaseModel):
    """Schema สำหรับ response (ไม่มี password!)"""
    user_id: int
    user_name: str
    email: str
    active: Optional[bool] = True
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# สำหรับใช้กับ login เดิม (backward compatible)
class Useresponse(UserResponse):
    """Alias สำหรับ backward compatibility"""
    pass