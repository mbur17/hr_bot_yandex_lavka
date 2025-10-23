from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.user import User


class UserCRUD:
    """Custom User CRUDs."""

    async def get_by_telegram_id(
        self, telegram_id: int, session: AsyncSession,
    ) -> User | None:
        """Get user by Telegram ID."""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id),
        )
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None

    async def get_by_login(
        self, login: str, session: AsyncSession,
    ) -> User | None:
        """Get user by login."""
        result = await session.execute(
            select(User).where(User.login == login),
        )
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None

    async def get_by_id(
        self, user_id: int, session: AsyncSession,
    ) -> User | None:
        """Get user by ID."""
        result = await session.execute(
            select(User).where(User.id == user_id),
        )
        user = result.scalar_one_or_none()
        return user if user and user.is_active else None


user_crud = UserCRUD()
