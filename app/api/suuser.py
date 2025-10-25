from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.schemas import suuser as schemas
from app.db.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

# OAuth2 scheme สำหรับ Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


# =============== Authentication Dependency ===============

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency สำหรับดึงข้อมูล User จาก Token

    ใช้ใน endpoint ที่ต้องการ authentication:
    @router.get("/profile")
    async def get_profile(current_user: models.User = Depends(get_current_user)):
        return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Verify และ decode token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    # ดึง username จาก token
    username: str = payload.get("sub")

    if username is None:
        raise credentials_exception

    # หา user จาก database
    user = db.query(models.User).filter(models.User.user_name == username).first()

    if user is None:
        raise credentials_exception

    # ตรวจสอบว่า user active หรือไม่
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


# =============== Endpoints ===============

@router.post("/login", response_model=schemas.Token, status_code=status.HTTP_200_OK)
async def login(credentials: schemas.Login, db: Session = Depends(get_db)):
    """
    Login endpoint - ตรวจสอบ username และ password แล้วคืน JWT Token

    - **username**: Username ของผู้ใช้
    - **password**: Password (จะถูก verify กับ hashed password ใน database)

    Returns:
        Token: access_token และ refresh_token
    """
    # หา user จาก username
    user = db.query(models.User).filter(
        models.User.user_name == credentials.username
    ).first()

    # ตรวจสอบว่า user มีอยู่ และ password ถูกต้อง
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # ตรวจสอบว่า user active หรือไม่
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # สร้าง Access Token และ Refresh Token
    access_token = create_access_token(
        data={"sub": user.user_name, "user_id": user.user_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.user_name, "user_id": user.user_id}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register endpoint - สร้าง user ใหม่

    - **user_name**: Username (3-20 ตัวอักษร)
    - **email**: Email address
    - **password**: Password (มากกว่า 6 ตัวอักษร, จะถูก hash อัตโนมัติ)
    """
    # ตรวจสอบว่า username ซ้ำหรือไม่
    existing_user = db.query(models.User).filter(
        models.User.user_name == user_data.user_name
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # สร้าง user ใหม่ พร้อม hash password
    new_user = models.User(
        user_name=user_data.user_name,
        email=user_data.email,
        password=hash_password(user_data.password),
        active=True,
        created_by="system",
        created_program="api"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """
    Get current user profile - ต้องใช้ Token

    ใช้ Token ที่ได้จาก /login ใน Header:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    return current_user


@router.get("/protected", response_model=dict)
async def protected_route(current_user: models.User = Depends(get_current_user)):
    """
    ตัวอย่าง Protected Endpoint - เข้าได้แค่ user ที่ login แล้วเท่านั้น

    ต้องส่ง Token ใน Header:
    Authorization: Bearer <your_token>
    """
    return {
        "message": f"Hello {current_user.user_name}!",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "status": "This is a protected route!"
    }
