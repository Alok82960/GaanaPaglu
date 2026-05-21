"""Application configuration using environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "GaanaPaglu"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Spotify
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    # JWT Authentication
    secret_key: str = "change-this-to-a-secure-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # Database
    database_url: str = "sqlite+aiosqlite:///./gaana_paglu.db"

    # AI Models
    model_name: str = "EleutherAI/gpt-neo-1.3B"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Rate Limiting
    rate_limit: str = "30/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        protected_namespaces = ("settings_",)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
