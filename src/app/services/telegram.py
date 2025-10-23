import httpx

from src.app.core.config import settings

TELEGRAM_BOT_TOKEN = settings.BOT_TOKEN


async def send_telegram_message(telegram_id: int, text: str) -> None:
    """Send message to user from bot."""
    if not TELEGRAM_BOT_TOKEN:
        print('BOT_TOKEN не задан в переменных окружения!')
        return False

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': telegram_id,
        'text': text,
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(url, data=data)
            response.raise_for_status()
    except Exception as e:
        print(f'Ошибка отправки сообщения в Telegram: {e}')
