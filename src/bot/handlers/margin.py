"""
Handler: margin — Input margine percentuale.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def handle_margin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce input testuale — routing in base allo stato della sessione."""
    # TODO M2: leggere stato sessione e instradare il messaggio
    # - awaiting_customer → parse nome/indirizzo cliente
    # - adjusting_margin → parse percentuale margine
    # - confirming_measures → parse misure manuali
    # - idle → suggerire /nuovo
    text = update.message.text
    log.info("handler.text_input", chat_id=update.effective_chat.id, text=text[:50])

    # Fallback: suggerisci comandi
    await update.message.reply_text(
        "Non ho capito. Usa /nuovo per creare un preventivo o /help per i comandi.",
    )
