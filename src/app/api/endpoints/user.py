from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.db import get_async_session
from src.app.schemas.user import (
    UserLoginRequest,
    UserLoginResponse,
    UserLogoutResponse,
)
from src.app.services.user import (
    authenticate_user,
    create_access_token,
)

router = APIRouter()


@router.post('/login/')
async def auth_user(
    response: Response,
    user_data: UserLoginRequest,
    session: AsyncSession = Depends(get_async_session),
) -> UserLoginResponse:
    """User login."""
    check = await authenticate_user(
        login=user_data.login,
        password=user_data.password,
        session=session)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid login credentials')
    access_token = create_access_token({'sub': str(check.id)})
    response.set_cookie(
        key='users_access_token', value=access_token, httponly=True)
    return {'access_token': access_token}


@router.post('/logout/')
async def logout_user(response: Response) -> UserLogoutResponse:
    """User logout."""
    response.delete_cookie(key='users_access_token')
    return {'message': 'Successful logout'}
