from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # AI API
    AI_API_KEY: str
    AI_BASE_URL: str = "https://api-ai.vivo.com.cn/v1"
    AI_MODEL: str = "Doubao-Seed-2.0-pro"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Image upload
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Rate limit (reserved for future use)
    RATE_LIMIT_PER_MINUTE: int = 30

    DATABASE_URL:str = "sqlite:///./qingyang.db"
    SECRET_KEY: str="your-secret-key-here-change-in-production"
    ALGORITHM: str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int= 30
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Settings()
