from pydantic import BaseModel

from src.app.models.user import UserRolesEnum


class TelegramAuthRequest(BaseModel):
    """Telegram auth request."""

    telegram_id: int


class TelegramAuthResponse(BaseModel):
    """Telegram auth response."""

    allowed: bool
    role: UserRolesEnum | None = None
