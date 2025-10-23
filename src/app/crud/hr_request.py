from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.const import HR_REQUEST_LIMIT, HR_REQUEST_OFFSET
from src.app.models.hr_request import HRRequest, HRRequestStatusEnum


class HRRequestCRUD:
    """Custom HRRequest CRUDs."""

    async def create_hr_request(
        self,
        user_id: int,
        message: str,
        session: AsyncSession,
    ) -> HRRequest:
        """Create new HRRequest."""
        new_req = HRRequest(
            user_id=user_id,
            message=message,
            status=HRRequestStatusEnum.NEW,
        )
        session.add(new_req)
        await session.commit()
        await session.refresh(new_req)
        return new_req

    async def get_user_requests(
        self,
        user_id: int,
        session: AsyncSession,
        offset: int = HR_REQUEST_OFFSET,
        limit: int = HR_REQUEST_LIMIT,
    ) -> list[HRRequest]:
        """Get user's HRRequests."""
        result = await session.execute(
            select(HRRequest)
            .where(HRRequest.user_id == user_id)
            .order_by(HRRequest.created_at.desc())
            .offset(offset)
            .limit(limit),
        )
        return result.scalars().all()


hr_request_crud = HRRequestCRUD()
