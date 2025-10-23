from collections import deque
from typing import Tuple

from telegram import Update
from telegram.ext import ContextTypes

from bot.backend_client import backend
from bot.config import get_settings
from bot.constants import ADMIN_PANEL_ROLES
from bot.keyboards import make_inline_kb
from bot.render import render_node

settings = get_settings()


async def check_user_allowed_and_role(user_id: int) -> Tuple[bool, bool]:
    """Check user permissions."""
    user = await backend.get_user(user_id)
    allowed = user.get('allowed', False)
    is_admin = user.get('role') in ADMIN_PANEL_ROLES
    return allowed, is_admin


async def _initialize_session_and_goto_root(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Initialize user session and go to root node."""
    ctx.user_data['stack'] = deque(maxlen=settings.STACK_LIMIT)
    user_id = update.effective_user.id
    allowed, is_admin = await check_user_allowed_and_role(user_id)

    if not allowed:
        msg = 'Доступ запрещен. Обратись к HR.'
        if update.message:
            await update.message.reply_text(msg)
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(msg)
        return

    ctx.user_data['is_admin'] = is_admin
    root_node = await backend.get_root_node()
    await goto_node(update, ctx, node_id=root_node['id'])


async def goto_node(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE, *,
    node_id: int,
) -> None:
    """Get node and navigate."""
    stack: deque = ctx.user_data.setdefault(
        'stack',
        deque(maxlen=settings.STACK_LIMIT),
    )
    node = await backend.get_node(node_id)

    if not stack or stack[-1] != node_id:
        stack.append(node_id)

    kb = make_inline_kb(
        node_buttons=node['buttons'],
        include_back=len(stack) > 1,
        is_admin=ctx.user_data.get('is_admin', False),
        user_id=update.effective_user.id,
        current_node_title=node['title'],
    )
    await render_node(update, node, kb)
