import asyncio
from datetime import datetime
from typing import Any

from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import Response
from wtforms import PasswordField

from src.app.admin.config import (
    NodeException,
    get_user_from_request,
)
from src.app.admin.filters import (
    hr_request_status_filter,
    layout_type_filter,
    user_role_filter,
)
from src.app.admin.validators import (
    check_image_attachment_to_node,
    check_no_cycle,
    check_node_by_id,
    check_role_and_handle_password,
    check_root_node,
    check_unique_button_order,
    check_unique_button_src_target,
    check_unique_image_filename_for_node,
    check_unique_image_order,
    node_has_children,
)
from src.app.core.const import DATE_TIME_FORMAT, MESSAGE_REPR_LEN
from src.app.crud.node import node_crud
from src.app.models.content import Button, Image, Node
from src.app.models.hr_request import HRRequest, HRRequestStatusEnum
from src.app.models.user import User, UserRolesEnum
from src.app.services.telegram import send_telegram_message


class UserAdmin(ModelView, model=User):
    """User admin class."""

    def is_accessible(self, request: Request) -> bool:
        """Grant admin access only."""
        loop = asyncio.get_event_loop()
        user = loop.run_until_complete(get_user_from_request(request=request))
        if user and user.role == UserRolesEnum.ADMIN:
            return True
        return False

    name = 'пользователя'
    name_plural = 'Пользователи'
    icon = 'fa-solid fa-user'
    edit_template = 'sqladmin/user_edit.html'
    create_template = 'sqladmin/user_create.html'

    column_list = [
        User.login,
        User.full_name,
        User.role,
        User.telegram_id,
        User.is_active,
    ]
    column_searchable_list = [
        User.login, User.full_name, User.telegram_id,
    ]
    column_sortable_list = [User.is_active]
    column_filters = [user_role_filter]
    column_details_list = [
        User.login,
        User.hashed_password,
        User.full_name,
        User.role,
        User.is_active,
        User.hr_requests,
    ]
    column_labels = {
        User.id: 'ID',
        User.login: 'Логин',
        User.hashed_password: 'Пароль',
        User.full_name: 'Полное имя',
        User.telegram_id: 'Telegram ID',
        User.is_active: 'Активирован',
        User.role: 'Роль',
        User.hr_requests: 'Запросы к HR',
    }
    form_columns = [
        User.login,
        User.role,
        User.hashed_password,
        User.full_name,
        User.telegram_id,
        User.is_active,
    ]
    form_overrides = {
        'hashed_password': PasswordField,
    }
    form_args = {
        'login': {'label': 'Логин'},
        'role': {'label': 'Роль'},
    }

    @action(
        name='import_users',
        label='Импорт пользователей',
        add_in_list=True,
        add_in_detail=False,
    )
    async def import_users(self, request: Request) -> Response:
        """Get form for import users."""
        from src.app.main import admin, templates
        return templates.TemplateResponse(
            'sqladmin/import_users.html',
            {
                'request': request,
                'model_view': self,
                'admin': admin,
            },
        )

    async def on_model_change(
        self,
        data: dict,
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:
        """Check password and apply logic."""
        password = data.get('hashed_password')
        new_role = data.get('role')
        old_role = model.role
        check_role_and_handle_password(
            data, is_created, old_role, new_role, password,
        )


class NodeAdmin(ModelView, model=Node):
    """Node admin class."""

    name = 'узел'
    name_plural = 'Узлы'
    icon = 'fa-solid fa-circle-nodes'

    column_list = [
        Node.id,
        Node.title,
        Node.layout_type,
        Node.parent,
        Node.is_active,
    ]
    column_searchable_list = [Node.title]
    column_sortable_list = [Node.parent, Node.is_active]
    column_filters = [layout_type_filter]
    column_labels = {
        Node.id: 'ID',
        Node.title: 'Название узла',
        Node.text: 'Текст узла',
        Node.layout_type: 'Тип отображения',
        Node.parent: 'Родительский узел',
        Node.children: 'Дочерние узлы',
        Node.outgoing_buttons: 'Кнопки',
        Node.is_active: 'Активирован',
    }
    form_columns = [
        Node.title,
        Node.layout_type,
        Node.text,
        Node.parent,
        Node.is_active,
    ]
    column_details_list = [
        Node.parent,
        Node.title,
        Node.text,
        Node.is_active,
        Node.children,
        Node.outgoing_buttons,
    ]

    edit_template = 'sqladmin/node_edit.html'
    create_template = 'sqladmin/node_create.html'

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: Node,
        is_created: bool,
        request: Request,
    ) -> None:
        """Validate node correctness on save."""
        parent_value = data.get('parent')
        parent_id = int(parent_value) if parent_value is not None else None
        node_id = model.id
        is_active = data.get('is_active')
        async with self.session_maker() as session:
            await check_no_cycle(session, node_id, parent_id)
            await check_root_node(session, parent_id, node_id)
            if not is_active:
                if await node_has_children(session, node_id):
                    raise ValueError('Узел имеет дочерние узлы.')

    async def delete_model(
            self, request: Request, pk: Any) -> None:
        """Delete model event."""
        async with self.session_maker() as session:
            if await node_has_children(session, int(pk)):
                raise NodeException(message='Узел имеет дочерние узлы.')
            root_node = await node_crud.get_root(session=session)
            if root_node is not None and root_node.id == int(pk):
                raise NodeException(message='Нельзя удалить корневой узел.')
        return await super().delete_model(request, pk)


class ButtonAdmin(ModelView, model=Button):
    """Button admin class."""

    name = 'кнопку'
    name_plural = 'Кнопки'
    icon = 'fa-solid fa-square'

    column_list = [
        Button.id,
        Button.label,
        Button.source_node_id,
        Button.source_node,
        Button.order,
        Button.target_node,
        Button.is_active,
    ]
    column_searchable_list = [Button.label]
    column_sortable_list = [Button.source_node_id, Button.is_active]
    column_labels = {
        Button.id: 'ID кнопки',
        Button.source_node: 'Прикреплена к узлу',
        Button.target_node: 'Ведет на узел',
        Button.source_node_id: 'ID исходного узла',
        Button.target_node_id: 'ID целевого узла',
        Button.label: 'Название кнопки',
        Button.order: 'Порядок отображения',
        Button.is_active: 'Активирована',
    }
    column_details_list = [
        Button.label,
        Button.source_node,
        Button.source_node_id,
        Button.order,
        Button.target_node,
        Button.target_node_id,
        Button.is_active,
    ]

    form_excluded_columns = [Button.is_active]

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: Button,
        is_created: bool,
        request: Request,
    ) -> None:
        """Validate button uniqueness and correctness on save."""
        source_node_raw = data.get('source_node')
        target_node_raw = data.get('target_node')
        order_raw = data.get('order')

        if source_node_raw is None or target_node_raw is None:
            raise ValueError('Выберите исходный и целевой узлы.')

        source_node_id = int(source_node_raw)
        target_node_id = int(target_node_raw)
        order = int(order_raw) if order_raw is not None else model.order
        exclude_id = model.id or None

        if source_node_id == target_node_id:
            raise ValueError('Кнопка не может вести в тот же узел.')

        async with self.session_maker() as session:
            await check_unique_button_order(
                session, source_node_id, order, exclude_id,
            )
            await check_unique_button_src_target(
                session, source_node_id, target_node_id, exclude_id,
            )


class ImageAdmin(ModelView, model=Image):
    """Image admin class."""

    can_edit = False

    name = 'изображение'
    name_plural = 'Изображения'
    icon = 'fa-solid fa-image'

    column_list = [
        Image.id,
        Image.file_name,
        'node.title',
        Image.order,
        'image_preview',
    ]
    column_searchable_list = [Image.file_name, 'node.title']
    column_sortable_list = ['node.title']
    column_labels = {
        Image.node_id: 'ID узла',
        'node.title': 'Прикреплено к узлу',
        Image.node: 'Прикреплено к узлу',
        Image.image_url: 'URL изображения',
        Image.file_name: 'Имя файла',
        Image.order: 'Порядок отображения',
        'image_preview': 'Просмотр',
    }
    form_excluded_columns = [Image.file_name]
    column_details_list = [
        Image.node_id,
        Image.node,
        Image.image_url,
        Image.file_name,
        Image.order,
    ]

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: Image,
        is_created: bool,
        request: Request,
    ) -> None:
        """Validate image and order uniqueness on save."""
        node_raw = data.get('node')
        if node_raw is None:
            raise ValueError(
                'Выберите узел, к которому относится изображение.',
            )

        node_id = int(node_raw)
        image_url = data.get('image_url', model.image_url)
        order = int(data.get('order', model.order))
        exclude_id = model.id if model.id else None

        if hasattr(image_url, 'filename') and image_url.filename:
            filename = image_url.filename
        else:
            filename = model.file_name

        if not filename or not filename.strip():
            raise ValueError('Выберите изображение для загрузки!')

        data['file_name'] = filename

        async with self.session_maker() as session:
            await check_unique_image_order(session, node_id, order, exclude_id)
            await check_unique_image_filename_for_node(
                session, node_id, filename, exclude_id,
            )
            node = await check_node_by_id(session, node_id)
            await check_image_attachment_to_node(
                node=node,
                session=session,
                is_created=is_created,
                exclude_id=exclude_id,
            )


class HRRequestAdmin(ModelView, model=HRRequest):
    """HRRequest admin class."""

    name = 'Вопрос'
    name_plural = 'Вопросы'
    icon = 'fa-solid fa-envelope'

    can_create = False
    can_delete = False

    column_list = [
        HRRequest.id,
        'user.full_name',
        HRRequest.message,
        HRRequest.status,
        HRRequest.created_at,
        HRRequest.replied_at,
    ]
    column_searchable_list = [HRRequest.message, 'user.full_name']
    column_sortable_list = [
        'user.full_name',
        HRRequest.status,
        HRRequest.created_at,
        HRRequest.replied_at,
    ]
    column_filters = [hr_request_status_filter]
    column_labels = {
        HRRequest.id: 'ID вопроса',
        HRRequest.user_id: 'ID пользователя',
        HRRequest.user: 'Пользователь',
        'user.full_name': 'Пользователь',
        HRRequest.message: 'Сообщение',
        HRRequest.status: 'Статус',
        HRRequest.hr_reply: 'Ответ',
        HRRequest.created_at: 'Дата вопроса',
        HRRequest.replied_at: 'Дата ответа',
    }
    column_formatters = {
        HRRequest.message: (
            lambda m, a: (
                m.message[:MESSAGE_REPR_LEN] +
                ('...' if len(m.message) > MESSAGE_REPR_LEN else '')
            )
        ),
        HRRequest.created_at: (
            lambda obj, _: (
                obj.created_at.strftime(
                    DATE_TIME_FORMAT,
                ) if obj.created_at else ''
            )
        ),
        HRRequest.replied_at: (
            lambda obj, _: (
                obj.replied_at.strftime(
                    DATE_TIME_FORMAT,
                ) if obj.replied_at else ''
            )
        ),
    }
    form_columns = [
        HRRequest.user,
        HRRequest.message,
        HRRequest.created_at,
        HRRequest.hr_reply,
    ]
    form_widget_args = {
        'user': {'readonly': True},
        'created_at': {'readonly': True},
        'message': {'readonly': True},
    }

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: HRRequest,
        is_created: bool,
        request: Request,
    ) -> None:
        """Change status and replied_at after hr_reply."""
        if model.hr_reply:
            raise ValueError('Можно ответить только один раз!')
        if (
            data.get('hr_reply') and
            str(data.get('status')) != HRRequestStatusEnum.ANSWERED.value
        ):
            data['status'] = HRRequestStatusEnum.ANSWERED.value
            data['replied_at'] = datetime.now()

    async def after_model_change(
        self,
        data: dict[str, Any],
        model: HRRequest,
        is_created: bool,
        request: Request,
    ) -> None:
        """Send HR reply to user."""
        if model.hr_reply and model.status == HRRequestStatusEnum.ANSWERED:
            text = f'Ответ от HR по вопросу #{model.id}:\n{model.hr_reply}'
            await send_telegram_message(model.user.telegram_id, text)
