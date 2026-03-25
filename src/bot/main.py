"""Serramentista Bot — Entry point"""
import logging
import sys

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import settings
from handlers.start import start_handler, connect_handler
from handlers.new_quote import new_quote_handler, customer_text_handler
from handlers.photo import photo_handler, measures_callback_handler
from handlers.voice import voice_handler
from handlers.commands import help_handler, status_handler, cancel_handler
from handlers.products import handle_product_callback
from handlers.extras import handle_extras_callback
from handlers.margin import handle_margin_callback, handle_margin_text
from handlers.confirm import handle_confirm_callback
from handlers.errors import error_handler
from services.session_service import SessionManager
from models.session import SessionState

# Logging
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Smista le callback inline keyboard in base al prefisso."""
    query = update.callback_query
    data = query.data or ""

    if data.startswith("measures:"):
        await measures_callback_handler(update, context)
    elif data.startswith("products:"):
        await handle_product_callback(update, context)
    elif data.startswith("extras:"):
        await handle_extras_callback(update, context)
    elif data.startswith("margin:"):
        await handle_margin_callback(update, context)
    elif data.startswith("confirm:"):
        await handle_confirm_callback(update, context)
    else:
        # Fallback: prova il vecchio handler misure
        await measures_callback_handler(update, context)


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Smista i messaggi di testo in base allo stato della sessione."""
    chat_id = update.effective_chat.id
    session = await SessionManager.get_session(chat_id)

    if not session:
        await update.message.reply_text(
            "👋 Non sei ancora collegato. Usa /start per iniziare."
        )
        return

    state = session.get("state", "idle")
    state_data = session.get("state_data", {})

    if state == SessionState.AWAITING_CUSTOMER.value:
        await customer_text_handler(update, context)
    elif state == SessionState.ADJUSTING_MARGIN.value and state_data.get("awaiting_custom_margin"):
        await handle_margin_text(update, context)
    else:
        await update.message.reply_text(
            "Non ho capito. Usa /nuovo per creare un preventivo o /help per i comandi.",
        )


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

    # Callback (inline keyboard buttons) — router centralizzato
    app.add_handler(CallbackQueryHandler(callback_router))

    # Testo libero — router basato sullo stato sessione
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    # Error handler globale
    app.add_error_handler(error_handler)

    logger.info("Bot avviato — in ascolto")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
