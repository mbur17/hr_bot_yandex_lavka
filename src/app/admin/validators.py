from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app.core.const import (
    GALLERY_IMAGE_NUM,
    MIN_PASSWORD_LEN,
    TEXT_IMAGE_NUM,
)
from src.app.crud.node import node_crud
from src.app.models import (
    Button,
    Image,
    Node,
    NodeLayoutTypeEnum,
    UserRolesEnum,
)
from src.app.services.user import get_password_hash


async def check_root_node(
    session: AsyncSession,
    new_parent_id: int | None,
    node_id: int | None = None,
) -> None:
    """Only one root node allowed."""
    if not new_parent_id:
        root_node = await node_crud.get_root(session=session)
        if root_node and (node_id is None or root_node.id != node_id):
            raise ValueError(
                '''
                Нельзя создавать больше одного корневого узла!\n
                Выберите "Родительский узел".
                ''',
            )


async def check_no_cycle(
    session: AsyncSession, node_id: int | None, new_parent_id: int | None,
) -> None:
    """Check that assigning a new parent does not create a cyclic reference."""
    if node_id is None or new_parent_id is None:
        return

    current_parent_id = new_parent_id
    while current_parent_id is not None:
        if current_parent_id == node_id:
            raise ValueError('Выбранный узел-родитель создаёт цикл в дереве!')
        result = await session.execute(
            select(Node.parent_id).where(Node.id == current_parent_id),
        )
        parent_row = result.first()
        if parent_row is None:
            break
        current_parent_id = parent_row[0]


async def check_unique_button_order(
    session: AsyncSession,
    source_node_id: int,
    order: int,
    exclude_id: int | None = None,
) -> None:
    """Check if button order is unique inside parent node."""
    query = select(Button).where(
        Button.source_node_id == source_node_id,
        Button.order == order,
    )
    if exclude_id:
        query = query.where(Button.id != exclude_id)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(
            'Кнопка с таким порядком уже существует для этого узла.',
        )


async def check_unique_image_order(
    session: AsyncSession,
    node_id: int,
    order: int,
    exclude_id: int | None = None,
) -> None:
    """Check if image order is unique for node."""
    query = select(Image).where(
        Image.node_id == node_id,
        Image.order == order,
    )
    if exclude_id:
        query = query.where(Image.id != exclude_id)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(
            'Изображение с таким порядком уже существует для этого узла.',
        )


async def check_unique_button_src_target(
        session: AsyncSession,
        source_node_id: int,
        target_node_id: int,
        exclude_id: int | None = None,
) -> None:
    """Check if button has unique src_node target_node pair."""
    query = select(Button).where(
        Button.source_node_id == source_node_id,
        Button.target_node_id == target_node_id,
    )
    if exclude_id:
        query = query.where(Button.id != exclude_id)
    result = await session.execute(query)
    existing = result.scalars().first()
    if existing:
        raise ValueError('Между этими двумя узлами уже есть кнопка!')


async def check_unique_image_filename_for_node(
    session: AsyncSession,
    node_id: int,
    file_name: str,
    exclude_id: int | None = None,
) -> None:
    """Check filename uniqueness."""
    query = select(Image).where(
        Image.node_id == node_id,
        Image.file_name == file_name,
    )
    if exclude_id:
        query = query.where(Image.id != exclude_id)
    result = await session.execute(query)
    existing = result.scalars().first()
    if existing:
        raise ValueError(
            'В этом узле уже есть изображение с таким именем файла.',
        )


async def check_node_by_id(session: AsyncSession, node_id: int) -> Node:
    """Get node by node.id or ValueError."""
    node = await session.get(Node, node_id)
    if (not node) or (not node.is_active):
        raise ValueError('Узел не найден!')
    return node


async def check_image_attachment_to_node(
    node: Node,
    session: AsyncSession,
    is_created: bool,
    exclude_id: int | None = None,
) -> None:
    """Validate image attachment due to layout_type of node."""
    if node.layout_type == NodeLayoutTypeEnum.text:
        raise ValueError('К узлу с типом TEXT нельзя прикреплять изображения.')

    images_q = select(Image).where(Image.node_id == node.id)
    if exclude_id:
        images_q = images_q.where(Image.id != exclude_id)
    images_count = len((await session.execute(images_q)).scalars().all())
    if is_created:
        images_count += 1

    if node.layout_type == (
        NodeLayoutTypeEnum.text_image and images_count > TEXT_IMAGE_NUM
    ):
        raise ValueError(
            'К узлу типа TEXT_IMAGE можно прикрепить только одно изображение.',
        )

    if node.layout_type == (
        NodeLayoutTypeEnum.gallery and images_count > GALLERY_IMAGE_NUM
    ):
        raise ValueError(
            'К узлу типа GALLERY можно прикрепить не более 10 изображений.',
        )


async def node_has_children(session: AsyncSession, pk: int) -> bool:
    """Check node has children."""
    children = select(Node).where(Node.parent_id == pk)
    if len((await session.execute(children)).scalars().all()) == 0:
        return False
    return True


def validate_and_set_password(data: dict[str, Any], password: str) -> None:
    """Validate password length and hash."""
    if len(password) < MIN_PASSWORD_LEN:
        raise ValueError('Пароль должен быть не менее 4 символов.')
    data['hashed_password'] = get_password_hash(password)


def check_role_and_handle_password(
    data: dict[str, Any],
    is_created: bool,
    old_role: str,
    new_role: str,
    password: Optional[str],
) -> None:
    """Apply logic to password field depend on context and role."""
    admin_roles = {UserRolesEnum.ADMIN.name, UserRolesEnum.MANAGER.name}
    user_role = UserRolesEnum.USER.name
    if new_role == user_role:
        data['hashed_password'] = None
        return
    if new_role in admin_roles:
        if is_created:
            if not password:
                raise ValueError(
                    'Пароль обязателен для роли Администратор или Менеджер.',
                )
            validate_and_set_password(data, password)
        elif old_role == UserRolesEnum.USER and not password:
            raise ValueError(
                'При смене роли на Администратор или Менеджер нужен пароль.',
            )
        elif password:
            validate_and_set_password(data, password)
        else:
            data.pop('hashed_password', None)
