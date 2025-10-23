from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.db import get_async_session
from src.app.crud.node import node_crud
from src.app.schemas.content import NodeResponse
from src.app.services.node import enrich_node

router = APIRouter()


@router.get('/nodes/root', response_model=NodeResponse)
async def get_root_node_view(
    session: AsyncSession = Depends(get_async_session),
    request: Request = None,
) -> NodeResponse:
    """Root node router."""
    node = await node_crud.get_root(session=session)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Node not found',
        )
    return await enrich_node(node, session, request)


@router.get('/nodes/{id}', response_model=NodeResponse)
async def get_node_view(
    node_id: int = Path(..., alias='id'),
    session: AsyncSession = Depends(get_async_session),
    request: Request = None,
) -> NodeResponse:
    """Node router."""
    node = await node_crud.get_by_id(node_id=node_id, session=session)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Node not found',
        )
    return await enrich_node(node, session, request)
