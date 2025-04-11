"""Application settings configuration."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

# Load .env file before initializing settings
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # Model
    MODEL_PATH: str

    # API
    API_HOST: str
    API_PORT: int

    # Dagster
    DAGSTER_HOME: str
    DAGSTER_WORKSPACE_PATH: str = "workspace.yaml"  # Default to workspace.yaml in project root

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def workspace_path(self) -> Path:
        """Get the absolute path to the Dagster workspace file."""
        if os.path.isabs(self.DAGSTER_WORKSPACE_PATH):
            return Path(self.DAGSTER_WORKSPACE_PATH)
        return Path(self.DAGSTER_HOME) / self.DAGSTER_WORKSPACE_PATH

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
