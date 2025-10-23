from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.db import get_async_session
from src.app.crud.hr_request import hr_request_crud
from src.app.crud.user import user_crud
from src.app.models.hr_request import HRRequest
from src.app.schemas.hr_request import HRRequestCreate, HRRequestGet
from src.app.services.telegram import send_telegram_message

router = APIRouter()


@router.post('/hr-request', status_code=status.HTTP_201_CREATED)
async def create_hr_request(
    hr_req: HRRequestCreate,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Create HRRequest obj and confirm to user."""
    user = await user_crud.get_by_telegram_id(
        telegram_id=hr_req.telegram_id, session=session,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found or inactive.',
        )
    new_req = await hr_request_crud.create_hr_request(
        user_id=user.id, message=hr_req.message, session=session,
    )
    text = f'Ваш вопрос #{new_req.id} зарегистрирован!\nОжидайте ответа от HR.'
    await send_telegram_message(user.telegram_id, text)


@router.get('/hr-requests', response_model=list[HRRequestGet])
async def get_user_hr_requests(
    telegram_id: int,
    offset: int = 0,
    limit: int = 5,
    session: AsyncSession = Depends(get_async_session),
) -> list[HRRequest]:
    """Get user HRRequest objects by Telegram ID."""
    user = await user_crud.get_by_telegram_id(
        telegram_id=telegram_id, session=session,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found or inactive.',
        )
    return await hr_request_crud.get_user_requests(
        user_id=user.id, session=session, offset=offset, limit=limit,
    )
