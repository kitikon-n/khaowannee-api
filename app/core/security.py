"""
Security utilities for password hashing, verification and JWT tokens
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings

# สร้าง password context สำหรับ bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password ด้วย bcrypt

    Args:
        password: รหัสผ่านแบบ plain text

    Returns:
        str: รหัสผ่านที่ถูก hash แล้ว

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)
        $2b$12$KIXxP5QY7Z8N9X... (60 ตัวอักษร)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    ตรวจสอบว่า password ตรงกับ hashed password หรือไม่

    Args:
        plain_password: รหัสผ่านแบบ plain text
        hashed_password: รหัสผ่านที่ถูก hash แล้ว

    Returns:
        bool: True ถ้า password ถูกต้อง, False ถ้าไม่ถูกต้อง

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============== JWT Token Functions ===============

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    สร้าง JWT Access Token

    Args:
        data: ข้อมูลที่จะเก็บใน token (เช่น user_id, username)
        expires_delta: เวลาหมดอายุ (ถ้าไม่ระบุ ใช้ค่าจาก settings)

    Returns:
        str: JWT token string

    Example:
        >>> token = create_access_token({"sub": "john_doe", "user_id": 123})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()

    # กำหนดเวลาหมดอายุ
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    # เพิ่มข้อมูลเวลาหมดอายุเข้าไปใน payload
    to_encode.update({
        "exp": expire,  # expiration time
        "iat": datetime.utcnow(),  # issued at time
        "type": "access"
    })

    # สร้าง JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    สร้าง JWT Refresh Token (อายุนานกว่า Access Token)

    Args:
        data: ข้อมูลที่จะเก็บใน token

    Returns:
        str: JWT refresh token string
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    ตรวจสอบและ decode JWT token

    Args:
        token: JWT token string

    Returns:
        Dict[str, Any]: Payload ของ token ถ้าถูกต้อง
        None: ถ้า token ไม่ถูกต้องหรือหมดอายุ

    Example:
        >>> token = create_access_token({"sub": "john_doe", "user_id": 123})
        >>> payload = verify_token(token)
        >>> print(payload)
        {'sub': 'john_doe', 'user_id': 123, 'exp': 1632840000, ...}
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None


def decode_token(token: str) -> Optional[str]:
    """
    Decode token และดึง username (sub) ออกมา

    Args:
        token: JWT token string

    Returns:
        str: Username ถ้า token ถูกต้อง
        None: ถ้า token ไม่ถูกต้อง
    """
    payload = verify_token(token)
    if payload:
        username: str = payload.get("sub")
        return username
    return None


# ตัวอย่างการใช้งาน:
if __name__ == "__main__":
    # ทดสอบ hash password
    original_password = "mySecurePassword123"

    # Hash password
    hashed = hash_password(original_password)
    print(f"Original: {original_password}")
    print(f"Hashed:   {hashed}")
    print(f"Length:   {len(hashed)} characters")

    # Verify password
    print(f"\nVerify correct password: {verify_password(original_password, hashed)}")
    print(f"Verify wrong password:   {verify_password('wrongPassword', hashed)}")
