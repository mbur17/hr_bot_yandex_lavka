from collections.abc import AsyncGenerator

from fastapi_storages import FileSystemStorage
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.app.core.config import get_db_url

DATABASE_URL = get_db_url()

image_storage = FileSystemStorage(path='node_images')


class Base(AsyncAttrs, DeclarativeBase):
    """Base declarative class."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        return f'{self.__name__.lower()}'

    id = Column(Integer, primary_key=True)


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables() -> None:
    """Create database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async session."""
    async with async_session_maker() as session:
        yield session
