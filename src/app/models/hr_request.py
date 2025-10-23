from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ENUM as PGENUM
from sqlalchemy.orm import relationship

from src.app.core.db import Base


class HRRequestStatusEnum(str, Enum):
    """Request status enum."""

    NEW = 'Новое'
    ANSWERED = 'Отвечено'


class HRRequest(Base):
    """HR request model."""

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(
        PGENUM(
            HRRequestStatusEnum,
            name='hr_request_status_enum',
            create_type=False,
        ),
        default=HRRequestStatusEnum.NEW,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.now)
    hr_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='hr_requests')

    def __str__(self) -> str:
        return f'Вопрос #{self.id}'

    def __repr__(self) -> str:
        return str(self)
