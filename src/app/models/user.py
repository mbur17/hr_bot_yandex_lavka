from enum import Enum
from typing import Any

from sqlalchemy import BigInteger, Boolean, Column, String, event
from sqlalchemy.dialects.postgresql import ENUM as PGENUM
from sqlalchemy.orm import relationship, sessionmaker, validates

from src.app.core.db import Base


class UserRolesEnum(str, Enum):
    """User roles enum."""

    ADMIN = 'Администратор'
    MANAGER = 'Менеджер'
    USER = 'Пользователь'


class User(Base):
    """User model."""

    login = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, default=None)
    telegram_id = Column(BigInteger)
    is_active = Column(Boolean, default=True)
    role = Column(
        PGENUM(
            UserRolesEnum,
            name='user_roles_enum',
            create_type=False,
        ),
        nullable=False,
        default=UserRolesEnum.USER,
    )

    hr_requests = relationship(
        'HRRequest',
        primaryjoin='User.id==HRRequest.user_id',
        back_populates='user',
    )

    @validates('hashed_password')
    def clear_user_password(
        self, key: str, value: str | None,
    ) -> str | None:
        """Clear user password."""
        if self.role == UserRolesEnum.USER:
            return None
        return value

    def __str__(self) -> str:
        return f'{self.full_name}'

    def __repr__(self) -> str:
        return str(self)


@event.listens_for(User, 'before_insert')
def validate_username(mapper: Any, connection: Any, target: Any) -> None:
    """Check username exists."""
    session = sessionmaker(bind=connection)()
    existing_user = session.query(User).filter_by(
        login=target.login).first()
    if existing_user:
        raise ValueError(f'Пользователь {target.login} уже существует.')
