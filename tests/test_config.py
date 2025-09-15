"""Test configuration module."""

import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_validation() -> None:
    """Test that settings require necessary fields."""
    # Test that empty strings fail validation
    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # No environment file, no defaults


def test_settings_defaults() -> None:
    """Test default values in settings."""
    settings = Settings(
        telegram_bot_token="test_token",
        gigachat_client_id="test_id", 
        gigachat_client_secret="test_secret"
    )
    
    assert settings.bot_username == "thecomrademajor_bot"
    assert settings.gigachat_scope == "GIGACHAT_API_PERS"
    assert settings.log_level == "INFO"
