from fastapi import APIRouter

from src.app.api.endpoints import (
    content_router,
    hr_request_router,
    import_user_router,
    telegram_auth_router,
    user_router,
)

# Главный маршрутизатор для версии API v1
v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(user_router)
v1_router.include_router(telegram_auth_router, tags=['bot'])
v1_router.include_router(content_router, tags=['bot'])
v1_router.include_router(hr_request_router, tags=['bot'])
v1_router.include_router(import_user_router, tags=['admin'])
