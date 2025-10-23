from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import get_auth_data
from src.app.core.const import JWT_LIFETIME
from src.app.core.db import get_async_session
from src.app.crud.user import user_crud
from src.app.models.user import User, UserRolesEnum

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_access_token(data: dict) -> str:
    """Create jwt token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=JWT_LIFETIME)
    to_encode.update({'exp': expire})
    auth_data = get_auth_data()
    return jwt.encode(
        to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])


def get_password_hash(password: str) -> str:
    """Return hashed password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    login: str,
    password: str,
    session: AsyncSession,
) -> User | None:
    """Authenticate user."""
    user = await user_crud.get_by_login(login=login, session=session)
    if not user or verify_password(
        plain_password=password, hashed_password=str(user.hashed_password),
    ) is False:
        return None
    return user


async def get_token(request: Request) -> str | None:
    """Get access token from cookies."""
    token = request.cookies.get('access_token')
    if not token:
        return None
    return token['access_token']


async def get_current_user(
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(get_token),
) -> User | None:
    """Get current user."""
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(
            token, auth_data['secret_key'],
            algorithms=[auth_data['algorithm']])
    except JWTError:
        return None

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        return None

    user_id = payload.get('sub')
    if not user_id:
        return None

    user = await user_crud.get_by_id(user_id=int(user_id), session=session)
    if not user:
        return None
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User | None:
    """Get current admin."""
    if not current_user or current_user.role != UserRolesEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )
    return current_user
