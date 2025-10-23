import asyncio
from typing import Dict, Optional

import asyncpg

from infra.data.fixtures import BUTTON, NODE

from src.app.core.config import settings

ROOT_ID = 1
ROOT_TITLE = 'Главное меню'


async def get_connection() -> asyncpg.Connection:
    """Функция подключения к базе данных."""
    return await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_SERVER,
    )


async def get_node_id_by_title(
    conn: asyncpg.Connection, title: str,
) -> Optional[int]:
    """Get root node id by its title."""
    return await conn.fetchval('SELECT id FROM node WHERE title=$1', title)


async def load_nodes(conn: asyncpg.Connection) -> None:
    """Load nodes in DB from fixtures."""
    root_db_id = await get_node_id_by_title(conn, ROOT_TITLE)
    if root_db_id is None:
        print(f'Root node with title "{ROOT_TITLE}" not found in database.')
        return None
    id_map = {ROOT_ID: root_db_id}

    nodes_to_insert = NODE.copy()
    inserted = set()

    while nodes_to_insert:
        progress = False
        for node in nodes_to_insert[:]:
            parent_id = node['parent_id']
            if parent_id is not None and parent_id not in id_map:
                continue
            db_parent_id = id_map[parent_id] if parent_id is not None else None
            await conn.execute(
                """
                INSERT INTO node (title, text, layout_type, parent_id)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (title) DO NOTHING
                """,
                node['title'], node['text'], node['layout_type'], db_parent_id,
            )
            db_id = await get_node_id_by_title(conn, node['title'])
            id_map[node['id']] = db_id
            nodes_to_insert.remove(node)
            inserted.add(node['id'])
            progress = True
        if not progress:
            raise Exception('Невозможно вставить некоторые узлы.')
    return id_map


async def load_buttons(
    conn: asyncpg.Connection, id_map: Dict[int, int],
) -> None:
    """Load buttons in DB from fixtures with mapping."""
    for btn in BUTTON:
        source_id = id_map[btn['source_node_id']]
        target_id = id_map[btn['target_node_id']]
        await conn.execute(
            """
            INSERT INTO button (label, source_node_id, target_node_id, "order")
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (source_node_id, target_node_id) DO NOTHING
            """,
            btn['label'], source_id, target_id, btn['order'],
        )


async def main() -> None:
    """Load fixtures."""
    conn = await get_connection()
    try:
        async with conn.transaction():
            id_map = await load_nodes(conn)
            if not id_map:
                print('Корневой узел не найден, загрузка кнопок отменена.')
                return
            await load_buttons(conn, id_map)
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
