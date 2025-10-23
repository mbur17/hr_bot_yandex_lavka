from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Project base settings."""

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int

    BOT_TOKEN: str

    app_title: str = 'HR Bot API'
    secret: str
    first_superuser_login: str
    first_superuser_password: str
    first_superuser_full_name: str
    root_node_name: str
    root_node_text: str

    class Config:
        """Load config from env file."""

        env_file = (Path(__file__).parents[3] / 'infra' / '.env').resolve()
        env_file_encoding = 'utf-8'
        extra = 'allow'


def get_auth_data() -> dict[str, str]:
    """Return auth settings."""
    return {'secret_key': settings.secret, 'algorithm': 'HS256'}


settings = Settings()


def get_db_url() -> str:
    """Return database url."""
    return (
        f'postgresql+asyncpg://{settings.POSTGRES_USER}:'
        f'{settings.POSTGRES_PASSWORD}@'
        f'{settings.POSTGRES_SERVER}:'
        f'{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
    )
