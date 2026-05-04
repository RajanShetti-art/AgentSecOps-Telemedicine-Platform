"""Configuration helpers for patient service."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads environment-driven settings for patient service."""

    app_name: str = Field(default="patient-service")
    app_version: str = Field(default="1.0.0")

    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    database_url: str = Field(default="", alias="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
if not settings.database_url:
    import os

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    if db_user and db_password and db_host and db_name:
        settings.database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5432/{db_name}"
