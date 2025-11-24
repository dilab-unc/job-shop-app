import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Job Shop Backend"
    api_prefix: str = "/api"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jobshop.db")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    echo_sql: bool = os.getenv("ECHO_SQL", "False").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


