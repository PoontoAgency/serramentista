"""
Handler: extras — Selezione voci extra.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def handle_extra_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce la selezione voci extra via inline keyboard callback."""
    # TODO M3: mostrare voci extra preimpostate, gestire selezione
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔧 Selezione voci extra in sviluppo — M3"
    )
    log.info("handler.extra_selection", data=query.data)
