from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    mongodb_url: str 
    database_name: str 
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expiration_hours: int

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
