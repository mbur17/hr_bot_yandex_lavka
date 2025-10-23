import logging
from typing import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from bot.constants import COMMON_BTNS, HR_PAGE
from bot.handlers import (
    handle_back,
    handle_home,
    handle_my_requests,
    handle_write_hr,
)
from bot.services import (
    _initialize_session_and_goto_root,
    goto_node,
)

CallbackHandler = Callable[
    [Update, ContextTypes.DEFAULT_TYPE], Awaitable[None],
]

CALLBACK_HANDLERS: dict[str, CallbackHandler] = {
    COMMON_BTNS['back']: handle_back,
    COMMON_BTNS['home']: handle_home,
    COMMON_BTNS['write_hr']: handle_write_hr,
    COMMON_BTNS['my_requests']: handle_my_requests,
}


async def on_callback_query(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle callbacks."""
    query = update.callback_query
    await query.answer()

    if 'stack' not in ctx.user_data or 'is_admin' not in ctx.user_data:
        await _initialize_session_and_goto_root(update, ctx)
        return

    data = query.data

    if ctx.user_data.get('waiting_for_hr_message'):
        if data in [COMMON_BTNS['back'], COMMON_BTNS['home']]:
            del ctx.user_data['waiting_for_hr_message']

    if data == 'hr_next':
        ctx.user_data['hr_page'] = ctx.user_data.get('hr_page', HR_PAGE) + 1
        await handle_my_requests(update, ctx)
        return

    if data == 'hr_prev':
        ctx.user_data['hr_page'] = max(
            ctx.user_data.get('hr_page', HR_PAGE) - 1, HR_PAGE,
        )
        await handle_my_requests(update, ctx)
        return

    if data == COMMON_BTNS['my_requests']:
        ctx.user_data['hr_page'] = HR_PAGE

    if data in CALLBACK_HANDLERS:
        await CALLBACK_HANDLERS[data](update, ctx)
        return

    if data.isdigit():
        await goto_node(update, ctx, node_id=int(data))
        return

    logging.warning(f'Получены неожиданные данные колбэка: {data}')
