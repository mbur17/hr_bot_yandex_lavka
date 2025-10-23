from enum import Enum
from typing import Any

from fastapi_storages.integrations.sqlalchemy import FileType
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import ENUM as PGENUM
from sqlalchemy.orm import relationship, sessionmaker, validates

from src.app.core.db import Base, image_storage


class NodeLayoutTypeEnum(str, Enum):
    """Форматы отображения информационного узла."""

    text = 'TEXT'
    text_image = 'TEXT_IMAGE'
    gallery = 'GALLERY'


class Node(Base):
    """Информационный узел."""

    title = Column(String, nullable=False, unique=True)
    text = Column(Text)
    layout_type = Column(
        PGENUM(NodeLayoutTypeEnum, name='layout_type_enum', create_type=False),
        nullable=False,
        default=NodeLayoutTypeEnum.text,
    )
    # Новый self-reference для дерева.
    parent_id = Column(Integer, ForeignKey('node.id'), nullable=True)

    parent = relationship(
        'Node',
        remote_side='Node.id',
        back_populates='children',
    )
    children = relationship(
        'Node',
        primaryjoin='Node.id==Node.parent_id',
        back_populates='parent',
    )
    # Кнопки, исходящие из этого узла.
    outgoing_buttons = relationship(
        'Button',
        primaryjoin=(
            '(and_(Node.id==Button.source_node_id, Button.is_active==True))'
        ),
        back_populates='source_node',
        cascade='all, delete-orphan',
        foreign_keys='Button.source_node_id',
    )
    is_active = Column(
        Boolean, default=True, nullable=False, server_default='True')

    # Изображения, связанные с этим узлом.
    images = relationship(
        'Image',
        back_populates='node',
        cascade='all, delete-orphan',
    )

    @validates('parent_id')
    def validate_parent_id_not_self(
        self, key: str, value: int | None,
    ) -> int | None:
        """Запретить ссылку на самого себя."""
        if value is not None and self.id is not None and value == self.id:
            raise ValueError('Узел не может быть родителем самого себя.')
        return value

    def __str__(self) -> str:
        return f'{self.title!r}'

    def __repr__(self) -> str:
        return str(self)


@event.listens_for(Node, 'before_insert')
def validate_node_title_unique(
        mapper: Any, connection: Any, target: Any) -> None:
    """Check node title unique."""
    session = sessionmaker(bind=connection)()
    existing_node = session.query(Node).filter_by(
        title=target.title).first()
    if existing_node:
        raise ValueError(f'Узел {target.title} уже существует.')


@event.listens_for(Node, 'before_delete')
def can_delete_node(mapper: Any, connection: Any, target: Any) -> None:
    """Check node delete."""
    if len(target.children) != 0:
        raise ValueError('Нельзя удалить узел с потомками.')
    if not target.parent_id:
        raise ValueError('Нельзя удалить корневой узел.')


class Button(Base):
    """Кнопка перехода между узлами."""

    source_node_id = Column(
        Integer, ForeignKey('node.id', ondelete='CASCADE'), index=True,
    )
    target_node_id = Column(
        Integer, ForeignKey('node.id', ondelete='CASCADE'), index=True,
    )
    label = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    # Узел, откуда ведёт кнопка.
    source_node = relationship(
        'Node',
        back_populates='outgoing_buttons',
        foreign_keys=[source_node_id],
    )

    # Узел, куда ведёт кнопка
    target_node = relationship(
        'Node',
        foreign_keys=[target_node_id],
        passive_deletes=True,
    )

    is_active = Column(
        Boolean, default=True, nullable=False, server_default='True')

    __table_args__ = (
        UniqueConstraint(
            'source_node_id', 'order', name='uq_button_source_node_order',
        ),
        UniqueConstraint(
            'source_node_id', 'target_node_id', name='uq_button_src_tgt',
        ),
        CheckConstraint(
            'source_node_id <> target_node_id', name='ck_button_no_self_link',
        ),
    )

    def __str__(self) -> str:
        return f'{self.label!r}'

    def __repr__(self) -> str:
        return str(self)


@event.listens_for(Button, 'before_insert')
def validate_button_label_unique(
        mapper: Any, connection: Any, target: Any) -> None:
    """Check button unique."""
    session = sessionmaker(bind=connection)()
    existing_button = session.query(Button).filter_by(
        source_node_id=target.source_node_id, label=target.label).first()
    if existing_button:
        raise ValueError(
            f'Кнопка {target.label} уже существует в узле.')


class Image(Base):
    """Изображение, связанное с узлом."""

    node_id = Column(Integer, ForeignKey('node.id'), index=True)
    image_url = Column(FileType(storage=image_storage))
    file_name = Column(String, nullable=False, index=True)
    order = Column(Integer, nullable=False)

    @property
    def image_preview(self) -> str:
        """Return image url."""
        return f'/media/{self.file_name}'

    # Узел, к которому относится изображение.
    node = relationship(
        'Node',
        back_populates='images',
    )

    __table_args__ = (
        UniqueConstraint(
            'node_id', 'order', name='uq_image_node_order',
        ),
        UniqueConstraint(
            'node_id', 'image_url', name='uq_image_node_image_url',
        ),
    )

    def __str__(self) -> str:
        return self.file_name

    def __repr__(self) -> str:
        return str(self)
