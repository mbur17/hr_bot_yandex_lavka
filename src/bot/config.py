from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки бота, загружаемые из переменных окружения или .env файла."""

    BOT_TOKEN: str
    BACKEND_URL: str
    STACK_LIMIT: int = 20
    STOP_WORDS: list[str]

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).parents[2] / 'infra' / '.env').resolve(),
        env_file_encoding='utf-8',
        extra='allow',
    )


def get_settings() -> Settings:
    """Получение экземпляра настроек."""
    return Settings()
