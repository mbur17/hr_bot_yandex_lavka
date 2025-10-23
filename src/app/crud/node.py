from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.content import Node


class NodeCRUD:
    """Custom Node CRUDs."""

    async def get_by_id(
        self, node_id: int, session: AsyncSession,
    ) -> Node | None:
        """Get node by ID."""
        result = await session.execute(
            select(Node).where(Node.id == node_id),
        )
        return result.scalar_one_or_none()

    async def get_root(self, session: AsyncSession) -> Node | None:
        """Get root node."""
        result = await session.execute(
            select(Node).where(Node.parent_id.is_(None)),
        )
        return result.scalar_one_or_none()


node_crud = NodeCRUD()
