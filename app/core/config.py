from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.constants import Environment


class Settings(BaseSettings):
    DATABASE_URL: str

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    APP_VERSION: str = "1.0.0"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env")
