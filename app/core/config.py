from pydantic_settings import BaseSettings
from pathlib import Path

# หา root directory ของโปรเจกต์
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Database
    database_url: str

    # Security
    secret_key: str
    debug: bool = False

    # JWT Settings
    jwt_secret_key: str = "happyC!rcl385DTSIN#y"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # Token หมดอายุใน 30 นาที
    refresh_token_expire_days: int = 7     # Refresh token หมดอายุใน 7 วัน

    # API Keys
    alpha_vantage_api_key: str = "demo"  # Default: demo key (limited)

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'

settings = Settings()
