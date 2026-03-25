"""
Serramentista Bot — Entry Point
Registra handlers e avvia il bot in polling o webhook mode.
"""

import logging

import structlog
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import settings
from handlers.start import start_command, connect_command
from handlers.commands import help_command, status_command, cancel_command
from handlers.new_quote import new_quote_command
from handlers.photo import handle_photo
from handlers.voice import handle_voice
from handlers.products import handle_product_selection
from handlers.extras import handle_extra_selection
from handlers.margin import handle_margin_input
from handlers.confirm import handle_confirm
from handlers.errors import error_handler


def configure_logging():
    """Configura structlog per log strutturati."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer() if settings.log_level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def main():
    """Avvia il bot."""
    configure_logging()
    log = structlog.get_logger()
    log.info("bot.starting", mode=settings.bot_mode)

    # Crea l'applicazione
    app = Application.builder().token(settings.telegram_bot_token).build()

    # --- Comandi ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("connect", connect_command))
    app.add_handler(CommandHandler("nuovo", new_quote_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stato", status_command))
    app.add_handler(CommandHandler("annulla", cancel_command))

    # --- Messaggi ---
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_margin_input,  # fallback per input testo (margine, cliente, misure manuali)
    ))

    # --- Callback inline keyboard ---
    app.add_handler(CallbackQueryHandler(handle_product_selection, pattern=r"^product:"))
    app.add_handler(CallbackQueryHandler(handle_extra_selection, pattern=r"^extra:"))
    app.add_handler(CallbackQueryHandler(handle_confirm, pattern=r"^confirm:"))
    app.add_handler(CallbackQueryHandler(handle_confirm, pattern=r"^measures:"))

    # --- Errori ---
    app.add_error_handler(error_handler)

    # Avvia
    if settings.bot_mode == "webhook":
        log.info("bot.webhook", url=settings.webhook_url)
        app.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path=f"webhook/{settings.telegram_bot_token}",
            webhook_url=f"{settings.webhook_url}/webhook/{settings.telegram_bot_token}",
        )
    else:
        log.info("bot.polling")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
