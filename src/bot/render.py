import logging

from telegram import InlineKeyboardMarkup, InputMediaPhoto, Update

from bot.constants import LAYOUT_GALLERY, LAYOUT_TEXT, LAYOUT_TEXT_IMAGE


async def render_text(
        update: Update, kb: InlineKeyboardMarkup, full_content: str,
) -> None:
    """Обработка текста."""
    await update.effective_chat.send_message(
        full_content, reply_markup=kb, parse_mode='HTML',
    )


async def render_text_image(
    update: Update,
    kb: InlineKeyboardMarkup,
    full_content: str,
    images: list,
) -> None:
    """Обработка текста с картинкой."""
    if images:
        image_url = images[0].get('image_url')
        if image_url and image_url.startswith('http'):
            await update.effective_chat.send_photo(
                photo=image_url,
                caption=full_content,
                reply_markup=kb,
                parse_mode='HTML',
            )
            return
        logging.warning(f'TEXT_IMAGE: битый или пустой url: {image_url}')
    await render_text(update, kb, full_content)


async def render_gallery(
    update: Update, kb: InlineKeyboardMarkup, images: list, message_title: str,
) -> None:
    """Обработка галереи."""
    media = []
    for img in images[:10]:
        image_url = img.get('image_url')
        if image_url and image_url.startswith('http'):
            media.append(InputMediaPhoto(image_url))
        else:
            logging.warning(f'Галерея: битый или пустой url: {image_url}')
    if media:
        await update.effective_chat.send_media_group(media)
        gallery_caption = f'<b>{message_title}</b>' if message_title else ''
        if gallery_caption:
            await update.effective_chat.send_message(
                gallery_caption,
                reply_markup=kb,
                parse_mode='HTML',
            )
    else:
        await update.effective_chat.send_message(
            'В галерее нет доступных изображений.',
            reply_markup=kb,
            parse_mode="HTML",
        )


async def render_node(
        update: Update,
        node: dict,
        kb: InlineKeyboardMarkup) -> None:
    """Отображает узел диалога в соответствии с его типом."""
    lt = node['layout_type']
    message_text = str(node.get('text') or '')
    message_title = str(node.get('title') or '')
    full_content = (
        f'<b>{message_title}</b>\n{message_text}'
        if message_title else message_text
    )

    if update.callback_query:
        message_to_edit = update.callback_query.message
        if lt == LAYOUT_TEXT and not getattr(message_to_edit, 'photo', None):
            await message_to_edit.edit_text(
                full_content,
                reply_markup=kb,
                parse_mode='HTML',
            )
            return

    if lt == LAYOUT_TEXT:
        await render_text(update, kb, full_content)
    elif lt == LAYOUT_TEXT_IMAGE:
        await render_text_image(
            update, kb, full_content, node.get('images', []),
        )
    elif lt == LAYOUT_GALLERY:
        await render_gallery(update, kb, node.get('images', []), message_title)
    else:
        await update.effective_chat.send_message(
            'Неизвестный формат узла.',
            reply_markup=kb,
            parse_mode='HTML',
        )
