"""Configuration management for OAIT."""

from typing import Literal
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenRouter API Configuration (REQUIRED - Only Cloud Dependency)
    openrouter_api_key: SecretStr
    openrouter_model: str = "google/gemini-3.0-pro"

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 7860

    # Local Faster-Whisper Configuration
    whisper_model_size: Literal["base", "small", "medium", "large"] = "base"
    whisper_device: str = "auto"
    whisper_compute_type: Literal["int8", "float16", "float32"] = "int8"

    # Database Configuration (Local SQLite)
    sqlite_db_path: str = "./memory/oait.db"

    # Audio Configuration
    audio_buffer_duration: float = 30.0  # seconds
    silence_threshold: float = 3.0  # seconds

    # Vision Configuration
    vision_polling_interval: float = 3.0  # seconds
    vision_change_threshold: float = 0.1  # 0.0 to 1.0

    # OODA Loop Configuration
    intervention_delay_base: float = 3.0  # seconds
    confidence_threshold: float = 0.7  # 0.0 to 1.0

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_file: str = "./logs/oait.log"

    # Development
    debug: bool = False
    reload: bool = False


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None
