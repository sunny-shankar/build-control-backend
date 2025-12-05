from pydantic_settings import BaseSettings

from app.common.constants import Environment


class Settings(BaseSettings):
    # DATABASE_URL: PostgresDsn

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    APP_VERSION: str = "1.0.0"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
