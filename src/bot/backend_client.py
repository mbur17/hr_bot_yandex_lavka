from typing import Any

import httpx

from bot.config import get_settings
from bot.constants import HR_PAGE, HR_PAGE_SIZE

settings = get_settings()


class BackendClient:
    """Клиент для взаимодействия с бэкенд API."""

    def __init__(self, base_url: str) -> None:
        """Инициализирует BackendClient."""
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip('/'),
            timeout=10,
        )

    async def close(self) -> None:
        """Закрывает соединение с клиентом."""
        await self._client.aclose()

    async def get_user(self, tg_id: int) -> dict[str, Any]:
        """Получает данные пользователя по Telegram ID."""
        r = await self._client.post(
            '/api/v1/auth/telegram',
            json={'telegram_id': tg_id},
        )
        r.raise_for_status()
        return r.json()

    async def get_root_node(self) -> dict[str, Any]:
        """Получает корневой узел диалога."""
        r = await self._client.get('/api/v1/nodes/root')
        r.raise_for_status()
        return r.json()

    async def get_node(self, node_id: int) -> dict[str, Any]:
        """Получает данные узла диалога по его ID."""
        r = await self._client.get(f'/api/v1/nodes/{node_id}')
        r.raise_for_status()
        return r.json()

    async def send_hr_request(self, tg_id: int, message: str) -> str:
        """Отправляет HR запрос."""
        r = await self._client.post(
            '/api/v1/hr-request',
            json={'telegram_id': tg_id, 'message': message},
        )
        r.raise_for_status()
        return r.json()

    async def get_hr_requests(
        self, tg_id: int, offset: int = HR_PAGE, limit: int = HR_PAGE_SIZE,
    ) -> list[dict]:
        """Get paginated list of HR-requests for user."""
        r = await self._client.get(
            '/api/v1/hr-requests',
            params={'telegram_id': tg_id, 'offset': offset, 'limit': limit},
        )
        r.raise_for_status()
        return r.json()


backend = BackendClient(settings.BACKEND_URL)
