from typing import List, Optional

from pydantic import BaseModel

from src.app.models.content import NodeLayoutTypeEnum


class ContentBase(BaseModel):
    """Базовая схема с поддержкой ORM и ID."""

    id: int

    class Config:
        """Поддержка ORM."""

        orm_mode = True


class ButtonResponse(ContentBase):
    """Button response."""

    label: str
    target_node_id: int
    order: int


class ImageResponse(ContentBase):
    """Image response."""

    image_url: str
    order: int


class ChildNodeResponse(ContentBase):
    """Child node response."""

    title: str
    text: Optional[str]
    layout_type: NodeLayoutTypeEnum
    parent_id: Optional[int]


class NodeResponse(ChildNodeResponse):
    """Node full response."""

    children: List[ChildNodeResponse]
    buttons: List[ButtonResponse]
    images: List[ImageResponse]
