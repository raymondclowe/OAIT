"""Basic unit tests for configuration."""

import pytest
from oait.config import Settings, get_settings, reset_settings


def test_settings_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings have correct default values."""
    reset_settings()
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    settings = Settings()
    
    # Accept either old or new model name (config may vary)
    assert settings.openrouter_model in ["google/gemini-3.0-pro", "google/gemini-3-pro-preview"]
    assert settings.server_host == "0.0.0.0"
    assert settings.server_port == 7860
    assert settings.whisper_model_size == "base"
    assert settings.silence_threshold == 3.0
    assert settings.vision_polling_interval == 3.0


def test_get_settings_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get_settings returns the same instance."""
    reset_settings()
    
    # Use monkeypatch to mock the environment
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key_123")
    
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
    assert settings1.openrouter_api_key.get_secret_value() == "test_key_123"
    
    reset_settings()


def test_reset_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that reset_settings clears the singleton."""
    reset_settings()
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    
    settings1 = get_settings()
    reset_settings()
    
    settings2 = get_settings()
    
    # Should be different instances after reset
    assert settings1 is not settings2
    
    reset_settings()
