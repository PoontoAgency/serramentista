"""
Handler: /help, /stato, /annulla
Comandi utility del bot.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra i comandi disponibili."""
    await update.message.reply_text(
        "🪟 *Serramentista — Comandi*\n\n"
        "/nuovo — Crea un nuovo preventivo\n"
        "/stato — Mostra lo stato corrente\n"
        "/annulla — Annulla operazione in corso\n"
        "/help — Questo messaggio\n\n"
        "📸 Invia una _foto_ per analizzare una finestra\n"
        "🎤 Invia una _nota vocale_ per aggiungere dettagli",
        parse_mode="Markdown",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra lo stato della sessione corrente."""
    # TODO M2: leggere stato da bot_sessions su Supabase
    await update.message.reply_text(
        "📊 *Stato corrente*\n\n"
        "Nessuna sessione attiva.\n"
        "Usa /nuovo per creare un preventivo.",
        parse_mode="Markdown",
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Annulla l'operazione corrente e resetta la sessione."""
    # TODO M2: reset sessione su Supabase
    await update.message.reply_text(
        "❌ Operazione annullata.\n"
        "La bozza del preventivo è stata salvata.\n\n"
        "Usa /nuovo per ricominciare.",
    )
    log.info("handler.cancel", chat_id=update.effective_chat.id)
