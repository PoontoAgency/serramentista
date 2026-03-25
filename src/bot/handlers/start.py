"""
Handler: /start e /connect
Gestisce il primo contatto e il collegamento account.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce /start — messaggio di benvenuto."""
    await update.message.reply_text(
        "🪟 *Benvenuto in Serramentista!*\n\n"
        "Sono il tuo assistente per i preventivi.\n"
        "Per iniziare, collega il tuo account con il comando:\n"
        "`/connect <token>`\n\n"
        "Il token lo trovi nella dashboard web, sezione Impostazioni.\n\n"
        "Comandi disponibili:\n"
        "/connect — Collega il tuo account\n"
        "/nuovo — Crea un nuovo preventivo\n"
        "/stato — Mostra lo stato corrente\n"
        "/annulla — Annulla operazione in corso\n"
        "/help — Aiuto",
        parse_mode="Markdown",
    )
    log.info("handler.start", chat_id=update.effective_chat.id)


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce /connect <token> — collega account Telegram alla dashboard."""
    if not context.args:
        await update.message.reply_text(
            "⚠️ Serve il token!\n\n"
            "Uso: `/connect <token>`\n"
            "Il token lo trovi nella dashboard web → Impostazioni → Telegram.",
            parse_mode="Markdown",
        )
        return

    token = context.args[0]
    chat_id = update.effective_chat.id

    # TODO M1: verificare token su Supabase, salvare chat_id
    log.info("handler.connect", chat_id=chat_id, token_prefix=token[:8])

    await update.message.reply_text(
        "🔗 Collegamento in corso...\n\n"
        "⚠️ _Funzionalità in sviluppo — M1_",
        parse_mode="Markdown",
    )
