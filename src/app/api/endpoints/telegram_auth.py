from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.db import get_async_session
from src.app.crud.user import user_crud
from src.app.schemas.telegram_auth import (
    TelegramAuthRequest,
    TelegramAuthResponse,
)

router = APIRouter()


@router.post('/auth/telegram', response_model=TelegramAuthResponse)
async def auth_telegram_user(
    data: TelegramAuthRequest,
    session: AsyncSession = Depends(get_async_session),
) -> TelegramAuthResponse:
    """Telegram auth router."""
    user = await user_crud.get_by_telegram_id(
        telegram_id=data.telegram_id, session=session,
    )
    return TelegramAuthResponse(
        allowed=bool(user),
        role=user.role if user else None,
    )
