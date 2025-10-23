import asyncio
from collections import deque

from check_swear import SwearingCheck
from telegram import Update
from telegram.ext import ContextTypes

from bot.backend_client import backend
from bot.config import get_settings
from bot.constants import (
    HR_PAGE,
    HR_PAGE_SIZE,
    MIN_MESSAGE_LEN,
    SWEAR_PREDICT,
    SWEAR_PROBA,
)
from bot.keyboards import make_nav_kb, make_pagination_kb
from bot.services import (
    _initialize_session_and_goto_root,
    check_user_allowed_and_role,
    goto_node,
)

settings = get_settings()
sch = SwearingCheck(stop_words=settings.STOP_WORDS)


async def handle_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    ctx.user_data.pop('waiting_for_hr_message', None)
    await _initialize_session_and_goto_root(update, ctx)


async def handle_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Go to the previous node in dialog stack."""
    stack: deque = ctx.user_data.get('stack')
    if stack and len(stack) > 1:
        stack.pop()
        await goto_node(update, ctx, node_id=stack[-1])


async def handle_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to the root dialog node."""
    ctx.user_data['stack'].clear()
    await _initialize_session_and_goto_root(update, ctx)


async def handle_write_hr(
    update: Update, ctx: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Prompt the user to write a new HR request."""
    ctx.user_data['waiting_for_hr_message'] = True
    kb = make_nav_kb()
    await update.callback_query.message.reply_text(
        'Напиши свой вопрос в свободной форме сообщением боту. HR увидит '
        'его и ответит тебе прямо здесь в чате. Пожалуйста, укажи детали, '
        'если это важно (например, дату, отдел и т.д).',
        reply_markup=kb,
    )


async def handle_my_requests(
    update: Update, ctx: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show user's HR requests."""
    user_id = update.effective_user.id
    page = ctx.user_data.get('hr_page', HR_PAGE)
    offset = page * HR_PAGE_SIZE

    try:
        requests_list = await backend.get_hr_requests(
            user_id, offset=offset, limit=HR_PAGE_SIZE + 1,
        )
    except Exception:
        await update.callback_query.message.reply_text(
            'Ошибка при получении вопросов. Попробуй позже.',
        )
        return

    if not requests_list:
        await update.callback_query.message.reply_text('Еще нет HR-вопросов.')
        return

    has_next = len(requests_list) > HR_PAGE_SIZE
    has_prev = page > 0
    display_list = requests_list[:HR_PAGE_SIZE]

    text = f'<b>Твои HR-вопросы (страница {page + 1}):</b>\n'
    for req in display_list:
        text += (
            f'#{req["id"]} | {req["status"]} | {req["created_at"][:10]}\n'
            f'Вопрос: {req["message"]}\n'
        )
        if req.get('hr_reply'):
            replied_at = (
                req['replied_at'][:10] if req.get('replied_at') else ''
            )
            text += f'Ответ ({replied_at}): {req["hr_reply"]}\n'
        text += '------\n'

    kb = make_pagination_kb(has_prev, has_next)
    await update.callback_query.message.reply_text(
        text, reply_markup=kb, parse_mode='HTML',
    )


async def handle_hr_message(
    update: Update,
    ctx: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle incoming user message as HR request if waiting."""
    user_id = update.effective_user.id
    allowed, is_admin = await check_user_allowed_and_role(user_id)
    ctx.user_data['is_admin'] = is_admin

    if not allowed:
        await update.message.reply_text('Доступ запрещен. Обратись к HR.')
        ctx.user_data.pop('waiting_for_hr_message', None)
        return

    if is_admin:
        await update.message.reply_text(
            'Пользователи с административной ролью не могут отправлять '
            'сообщения HR через бота.',
        )
        ctx.user_data.pop('waiting_for_hr_message', None)
        await handle_home(update, ctx)

    if ctx.user_data.get('waiting_for_hr_message'):
        message_text = update.message.text
        message_text_raw = message_text.strip().lower()
        if len(message_text_raw) < MIN_MESSAGE_LEN:
            await update.message.reply_text(
                'Пожалуйста, опиши свой вопрос чуть подробнее '
                '(минимум 30 символов).',
            )
            return
        if (
            sch.predict(message_text_raw)[0] == SWEAR_PREDICT or
            sch.predict_proba(message_text_raw)[0] >= SWEAR_PROBA
        ):
            await update.message.reply_text(
                'Сообщение вероятно содержит грубые выражения. '
                'Пожалуйста, переформулируй.',
            )
            return
        await backend.send_hr_request(user_id, message_text)
        ctx.user_data.pop('waiting_for_hr_message', None)
        await asyncio.sleep(3)
        await handle_home(update, ctx)
