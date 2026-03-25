"""
Handler: confirm — Conferma preventivo e generazione PDF.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce conferma/modifica da inline keyboard (misure e preventivo finale)."""
    query = update.callback_query
    await query.answer()
    data = query.data

    # TODO M2: measures:confirm, measures:redo, measures:manual
    # TODO M3: confirm:generate_pdf, confirm:edit_margin, confirm:edit_extras

    log.info("handler.confirm", data=data)
    await query.edit_message_text(
        "⚠️ _Conferma in sviluppo_",
        parse_mode="Markdown",
    )
