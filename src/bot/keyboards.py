from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.config import get_settings
from bot.constants import COMMON_BTNS, HR_QUESTION_NODE_TITLE

settings = get_settings()


def make_inline_kb(
    node_buttons: List[Dict], *,
    include_back: bool = True,
    is_admin: bool = False,
    user_id: int | None = None,
    current_node_title: str,
) -> InlineKeyboardMarkup:
    """Создает клавиатуру для Telegram бота."""
    rows: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(
            btn['label'],
            callback_data=str(btn['target_node_id']))] for btn in node_buttons
    ]

    if current_node_title.strip().lower() == HR_QUESTION_NODE_TITLE:
        rows.append([InlineKeyboardButton(COMMON_BTNS['write_hr'],
                    callback_data=COMMON_BTNS['write_hr'])])
        rows.append([InlineKeyboardButton(COMMON_BTNS['my_requests'],
                    callback_data=COMMON_BTNS['my_requests'])])

    if is_admin and user_id is not None:
        rows.append([
            InlineKeyboardButton(
                text='Админ‑панель',
                web_app=WebAppInfo(
                    url=f'{settings.BACKEND_URL}admin'),
            ),
        ])

    common_buttons_row_titles = []
    if include_back:
        common_buttons_row_titles.append(COMMON_BTNS['back'])
    common_buttons_row_titles.append(COMMON_BTNS['home'])

    if common_buttons_row_titles:
        rows.append([InlineKeyboardButton(title, callback_data=title)
                    for title in common_buttons_row_titles])

    return InlineKeyboardMarkup(rows)


def make_nav_kb() -> InlineKeyboardMarkup:
    """Return inline keyboard with 'Back' and 'Home' buttons."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            COMMON_BTNS['back'], callback_data=COMMON_BTNS['back'],
        )],
        [InlineKeyboardButton(
            COMMON_BTNS['home'], callback_data=COMMON_BTNS['home'],
        )],
    ])


def make_pagination_kb(has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    """Return inline keyboard with 'Back', 'Next' and 'Home' buttons."""
    buttons = []
    if has_prev:
        buttons.append(
            InlineKeyboardButton(COMMON_BTNS['back'], callback_data='hr_prev'),
        )
    buttons.append(
        InlineKeyboardButton(
            COMMON_BTNS['home'], callback_data=COMMON_BTNS['home'],
        ),
    )
    if has_next:
        buttons.append(
            InlineKeyboardButton(COMMON_BTNS['next'], callback_data='hr_next'),
        )
    return InlineKeyboardMarkup([buttons])
