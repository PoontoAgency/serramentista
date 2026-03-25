"""
Handler: errors — Gestione errori globale.
"""

import html
import traceback

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce errori non catturati — logga e invia messaggio user-friendly."""
    log.error(
        "bot.error",
        error=str(context.error),
        traceback=traceback.format_exception(
            None, context.error, context.error.__traceback__
        ),
    )

    # Invia messaggio user-friendly se possibile
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Si è verificato un errore.\n"
                "Riprova tra qualche secondo.\n\n"
                "Se il problema persiste, usa /annulla e ricomincia.",
            )
        except Exception:
            pass  # Se anche questo fallisce, non possiamo fare nulla
