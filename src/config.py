import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base configuration using Pydantic Settings"""

    # App settings
    APP_NAME: str = "Ultimate Card Verification System"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Email
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_FROM_NAME: Optional[str] = None

    # Static files
    STATIC_DIR: str = "src/static"
    TEMPLATES_DIR: str = "src/templates"

    # File uploads
    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"xml"}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


class DevelopmentSettings(Settings):
    """Development configuration"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"


class TestSettings(Settings):
    """Test configuration"""
    DEBUG: bool = True
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///:memory:"
    SECRET_KEY: str = "test-secret-key"


class ProductionSettings(Settings):
    """Production configuration"""
    DEBUG: bool = False
    # Database URL should be set via environment variable
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@192.168.1.110/karty?charset=utf8"
    )


# Configuration factory
def get_settings() -> Settings:
    """Get settings based on APP_ENV environment variable"""
    env = os.getenv("APP_ENV", "dev")

    settings_map = {
        "dev": DevelopmentSettings,
        "test": TestSettings,
        "prod": ProductionSettings,
    }

    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


# Global settings instance
settings = get_settings()
