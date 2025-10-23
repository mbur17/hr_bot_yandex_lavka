from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.db import get_async_session
from src.app.models.user import User
from src.app.services.import_user import import_users_from_excel
from src.app.services.user import get_current_admin_user

router = APIRouter()


@router.post('/import-users/upload')
async def import_users_upload(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    current_admin_user: User = Depends(get_current_admin_user),
) -> RedirectResponse:
    """Import users from excel file."""
    file_bytes = await file.read()
    imported_count = await import_users_from_excel(file_bytes, session)
    return RedirectResponse(
        url='/admin/user/list?imported={}'.format(imported_count),
        status_code=status.HTTP_303_SEE_OTHER,
    )
