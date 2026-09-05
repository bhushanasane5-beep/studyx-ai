"""Application configuration for AI provider settings."""

from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from the backend environment."""

    nvidia_api_key: SecretStr
    nvidia_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("nvidia_model")
    @classmethod
    def validate_nvidia_model(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("NVIDIA_MODEL must be set")
        return value


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
