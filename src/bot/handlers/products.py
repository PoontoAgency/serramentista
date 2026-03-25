"""
Handler: products — Selezione prodotti inline keyboard.
"""

import structlog
from telegram import Update
from telegram.ext import ContextTypes

log = structlog.get_logger()


async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce la selezione prodotti via inline keyboard callback."""
    # TODO M3: leggere catalogo, mostrare prodotti per categoria/tier
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📦 Selezione prodotti in sviluppo — M3"
    )
    log.info("handler.product_selection", data=query.data)
