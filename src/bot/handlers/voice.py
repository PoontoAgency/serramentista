"""
Handler: voice — Ricezione note vocali e trascrizione.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce la ricezione di una nota vocale → trascrizione Whisper."""
    # TODO M2: scaricare audio, inviare a Whisper, salvare trascrizione
    await update.message.reply_text(
        "🎤 Nota vocale ricevuta!\n\n"
        "⚠️ _Trascrizione in sviluppo — M2_",
        parse_mode="Markdown",
    )
    log.info("handler.voice", chat_id=update.effective_chat.id)
