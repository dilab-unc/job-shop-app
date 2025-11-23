from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    app_name: str = "Job Shop Backend"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./jobshop.db"
    debug: bool = False
    echo_sql: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


