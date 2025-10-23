import logging

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.backend_client import backend
from bot.callbacks import on_callback_query
from bot.config import get_settings
from bot.handlers import handle_hr_message, handle_start

settings = get_settings()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)


async def on_shutdown(application: Application) -> None:
    """Gracefully closes the backend connection on application shutdown."""
    await backend.close()


def main() -> None:
    """Запускает приложение."""
    application = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .concurrent_updates(True)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.add_handler(CommandHandler('start', handle_start))
    application.add_handler(CommandHandler('menu', handle_start))
    application.add_handler(CallbackQueryHandler(on_callback_query))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_hr_message))

    logging.info('Bot starting…')
    application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
