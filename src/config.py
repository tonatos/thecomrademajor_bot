"""Configuration settings for the bot."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., description="Telegram bot token")
    bot_username: str = Field(default="thecomrademajor_bot", description="Bot username")

    # GigaChat API Configuration
    gigachat_client_id: str = Field(..., description="GigaChat client ID")
    gigachat_client_secret: str = Field(..., description="GigaChat client secret")
    gigachat_scope: str = Field(
        default="GIGACHAT_API_PERS", description="GigaChat scope"
    )

    # Bot Configuration
    log_level: str = Field(default="INFO", description="Logging level")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


def create_settings() -> Settings:
    """Create settings instance with proper error handling."""
    import os
    
    # Проверяем, есть ли переменные окружения (например, в Docker)
    if all(os.getenv(var) for var in ["TELEGRAM_BOT_TOKEN", "GIGACHAT_CLIENT_ID", "GIGACHAT_CLIENT_SECRET"]):
        # Если переменные окружения есть, создаем settings без .env файла
        return Settings(_env_file=None)  # type: ignore[call-arg]
    
    # Иначе пробуем загрузить из .env файла
    try:
        return Settings()  # type: ignore[call-arg]
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        print("💡 Убедитесь, что создан файл .env с необходимыми переменными:")
        print("   - TELEGRAM_BOT_TOKEN")
        print("   - GIGACHAT_CLIENT_ID")
        print("   - GIGACHAT_CLIENT_SECRET")
        print("📖 Подробные инструкции в START.md")

        # Fallback for testing without .env file
        return Settings(  # type: ignore[call-arg]
            telegram_bot_token="test_token",
            gigachat_client_id="test_id",
            gigachat_client_secret="test_secret",
        )


# Create settings instance
settings = create_settings()
