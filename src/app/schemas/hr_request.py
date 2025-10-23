from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.app.models.hr_request import HRRequestStatusEnum


class HRRequestCreate(BaseModel):
    """HRRequest request."""

    telegram_id: int
    message: str


class HRRequestGet(BaseModel):
    """HRRequest representation."""

    id: int
    message: str
    status: HRRequestStatusEnum
    created_at: datetime
    hr_reply: Optional[str] = None
    replied_at: Optional[datetime] = None

    class Config:
        """Поддержка ORM."""

        orm_mode = True
