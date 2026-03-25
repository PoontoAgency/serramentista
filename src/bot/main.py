"""Serramentista Bot — Entry point"""
import logging
import sys

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import settings
from handlers.start import start_handler, connect_handler
from handlers.new_quote import new_quote_handler, customer_text_handler
from handlers.photo import photo_handler, measures_callback_handler
from handlers.voice import voice_handler
from handlers.commands import help_handler, status_handler, cancel_handler
from handlers.errors import error_handler

# Logging
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Avvia il bot in polling mode"""
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN non configurato")
        sys.exit(1)

    logger.info("Avvio Serramentista Bot...")

    app = ApplicationBuilder().token(settings.telegram_bot_token).build()

    # Comandi
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("connect", connect_handler))
    app.add_handler(CommandHandler("nuovo", new_quote_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("stato", status_handler))
    app.add_handler(CommandHandler("annulla", cancel_handler))

    # Foto
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    # Note vocali
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    # Callback (inline keyboard buttons)
    app.add_handler(CallbackQueryHandler(measures_callback_handler))

    # Testo libero (per inserimento cliente — solo quando in stato AWAITING_CUSTOMER)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, customer_text_handler))

    # Error handler globale
    app.add_error_handler(error_handler)

    logger.info("Bot avviato — in ascolto")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
