"""
Configuration Management
========================
Centralized configuration management using environment variables.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration from environment variables."""

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "nba_analytics")

    # NBA API
    NBA_API_RATE_LIMIT: int = int(os.getenv("NBA_API_RATE_LIMIT", "600"))

    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Data Quality
    DQ_CRITICAL_THRESHOLD: float = float(os.getenv("DQ_CRITICAL_THRESHOLD", "0.95"))
    DQ_WARNING_THRESHOLD: float = float(os.getenv("DQ_WARNING_THRESHOLD", "0.90"))

    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @classmethod
    def get(cls, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value by key."""
        return getattr(cls, key, default)
