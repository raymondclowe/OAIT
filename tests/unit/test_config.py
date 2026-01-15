"""Basic unit tests for configuration."""

import pytest
from oait.config import Settings, get_settings, reset_settings


def test_settings_default_values() -> None:
    """Test that settings have correct default values."""
    reset_settings()
    settings = Settings(openrouter_api_key="test_key")
    
    assert settings.openrouter_model == "google/gemini-3.0-pro"
    assert settings.server_host == "0.0.0.0"
    assert settings.server_port == 7860
    assert settings.whisper_model_size == "base"
    assert settings.silence_threshold == 3.0
    assert settings.vision_polling_interval == 3.0


def test_get_settings_singleton() -> None:
    """Test that get_settings returns the same instance."""
    reset_settings()
    
    # Mock the environment or use test values
    import os
    os.environ["OPENROUTER_API_KEY"] = "test_key_123"
    
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
    assert settings1.openrouter_api_key == "test_key_123"
    
    # Cleanup
    del os.environ["OPENROUTER_API_KEY"]
    reset_settings()


def test_reset_settings() -> None:
    """Test that reset_settings clears the singleton."""
    import os
    os.environ["OPENROUTER_API_KEY"] = "test_key"
    
    settings1 = get_settings()
    reset_settings()
    
    settings2 = get_settings()
    
    # Should be different instances after reset
    assert settings1 is not settings2
    
    # Cleanup
    del os.environ["OPENROUTER_API_KEY"]
    reset_settings()
