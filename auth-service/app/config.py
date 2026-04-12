"""Configuration helpers for auth service."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads environment-driven settings for the service."""

    app_name: str = Field(default="auth-service")
    app_version: str = Field(default="1.0.0")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=60, alias="JWT_EXPIRE_MINUTES")
    database_url: str = Field(default="", alias="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
