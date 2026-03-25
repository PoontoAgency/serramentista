"""
Handler: foto — Ricezione foto e analisi AI.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce la ricezione di una foto → analisi marker AI."""
    # TODO M2: verificare stato sessione (deve essere awaiting_photo)
    # TODO M2: scaricare foto, pre-processing, upload su Storage
    # TODO M2: chiamare VisionService per analisi GPT-4o
    # TODO M2: mostrare risultato con inline keyboard conferma/correggi
    await update.message.reply_text(
        "📸 Foto ricevuta!\n\n"
        "⚠️ _Analisi AI in sviluppo — M2_",
        parse_mode="Markdown",
    )
    log.info("handler.photo", chat_id=update.effective_chat.id)
