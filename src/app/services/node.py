import os
from typing import NoReturn

from fastapi import HTTPException, Request, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.content import Node
from src.app.schemas.content import (
    ButtonResponse,
    ChildNodeResponse,
    ImageResponse,
    NodeResponse,
)


def make_full_url(image_url: str, request: Request) -> str:
    """Create full url for image."""
    if not image_url:
        return ''
    if image_url.startswith('http'):
        return image_url
    base_url = str(request.base_url).rstrip('/')
    filename = os.path.basename(image_url)
    return f'{base_url}/media/{filename}'


async def enrich_node(
    node: Node, session: AsyncSession, request: Request,
) -> NodeResponse | NoReturn:
    """Дополнить узел связанными кнопками и изображениями."""
    if not node.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Node not found.',
        )
    await session.refresh(node, attribute_names=['outgoing_buttons', 'images'])

    buttons = sorted([
        ButtonResponse(
            id=btn.id,
            label=btn.label,
            target_node_id=btn.target_node_id,
            order=btn.order,
        )
        for btn in node.outgoing_buttons
    ], key=lambda b: b.order)

    images = sorted([
        ImageResponse(
            id=img.id,
            image_url=make_full_url(img.image_url, request),
            order=img.order,
        )
        for img in node.images
    ], key=lambda i: i.order)

    get_children = await session.execute(
        select(Node).where(
            and_(
                Node.parent_id == node.id,
                Node.is_active),
            ),
        )

    children = [ChildNodeResponse(
        id=child.id,
        title=child.title,
        text=child.text,
        layout_type=child.layout_type,
        parent_id=child.parent_id,
        # buttons=child_buttons,
        # images=child.images,
    ) for child in get_children.scalars()]

    return NodeResponse(
        id=node.id,
        title=node.title,
        text=node.text,
        layout_type=node.layout_type,
        parent_id=node.parent_id,
        children=children,
        buttons=buttons,
        images=images,
    )
