from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound

from src.app.core.config import settings
from src.app.core.db import async_session_maker
from src.app.models import Node, NodeLayoutTypeEnum, User, UserRolesEnum
from src.app.services.user import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize application lifespan events."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.role == UserRolesEnum.ADMIN),
        )
        admin = result.scalar()
        result = await session.execute(
            select(Node).where(Node.parent_id.is_(None)),
        )
        try:
            node = result.scalar_one_or_none()
        except MultipleResultsFound as e:
            print(f'В таблице Node больше одного корневого узла {e}')
            raise SystemExit
        if not node:
            root_node = Node(
                parent_id=None,
                title=settings.root_node_name,
                text=settings.root_node_text,
                layout_type=NodeLayoutTypeEnum.text,
            )
            session.add(root_node)
            await session.commit()

        if not admin:
            admin_user = User(
                login=settings.first_superuser_login,
                full_name=settings.first_superuser_full_name,
                hashed_password=get_password_hash(
                    settings.first_superuser_password,
                ),
                role=UserRolesEnum.ADMIN,
            )
            session.add(admin_user)
            await session.commit()
    yield
