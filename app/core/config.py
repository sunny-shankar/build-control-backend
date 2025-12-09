import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.constants import Environment


class Settings(BaseSettings):
    DATABASE_URL: str

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    APP_VERSION: str = "1.0.0"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # JWT Settings
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OTP Settings
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3

    model_config = SettingsConfigDict(env_file=".env")
