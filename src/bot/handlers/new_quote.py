"""
Handler: /nuovo — Avvia un nuovo preventivo.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def new_quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Avvia il flusso di un nuovo preventivo."""
    # TODO M2: verificare che l'account sia collegato
    # TODO M2: creare quote draft su Supabase
    # TODO M2: transizione stato → awaiting_customer
    await update.message.reply_text(
        "📋 *Nuovo preventivo*\n\n"
        "Per chi è il preventivo?\n"
        "Scrivi _nome e indirizzo_ del cliente.\n\n"
        "Esempio: `Mario Rossi, Via Roma 12, Milano`",
        parse_mode="Markdown",
    )
    log.info("handler.new_quote", chat_id=update.effective_chat.id)
