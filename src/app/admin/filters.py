from typing import Any, List, Tuple

from sqladmin.filters import StaticValuesFilter
from starlette.requests import Request


class CustomEnumFilter(StaticValuesFilter):
    """Custom filter for ENUM fields."""

    async def lookups(
        self,
        request: Request,
        model: Any,
        run_query: Any,
    ) -> List[Tuple[str, str]]:
        """Return available values for filtering."""
        return self.values


user_role_filter = CustomEnumFilter(
    column='role',
    values=[
        ('ADMIN', 'Администратор'),
        ('MANAGER', 'Менеджер'),
        ('USER', 'Пользователь'),
    ],
    title='Роль',
    parameter_name='role',
)

layout_type_filter = CustomEnumFilter(
    column='layout_type',
    values=[
        ('text', 'Текст'),
        ('text_image', 'Текст с картинкой'),
        ('gallery', 'Галерея'),
    ],
    title='Тип контента',
    parameter_name='layout_type',
)

hr_request_status_filter = CustomEnumFilter(
    column='status',
    values=[
        ('NEW', 'Новое'),
        ('ANSWERED', 'Отвечено'),
    ],
    title='Статус запроса',
    parameter_name='status',
)
