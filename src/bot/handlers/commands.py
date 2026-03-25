"""Handler comandi utility: /stato, /annulla, /help"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from models.session import SessionState
from services.session_service import SessionManager
from utils.messages import MSG_HELP, MSG_STATE_IDLE, MSG_STATE_ACTIVE, MSG_CANCELLED, MSG_NOT_CONNECTED

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /help"""
    if not update.message:
        return
    await update.message.reply_text(MSG_HELP, parse_mode="Markdown")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /stato — mostra stato sessione corrente"""
    if not update.message:
        return

    chat_id = update.effective_chat.id
    session = await SessionManager.get_or_create(chat_id)

    if session is None:
        await update.message.reply_text(MSG_NOT_CONNECTED, parse_mode="Markdown")
        return

    state = session.get("state", "idle")
    state_data = session.get("state_data", {})

    if state == SessionState.IDLE.value:
        await update.message.reply_text(MSG_STATE_IDLE, parse_mode="Markdown")
    else:
        state_labels = {
            "awaiting_customer": "In attesa nome cliente",
            "awaiting_photo": "In attesa foto finestra",
            "confirming_measures": "Conferma misure",
            "selecting_products": "Selezione prodotti",
            "selecting_extras": "Selezione voci extra",
            "adjusting_margin": "Regolazione margine",
            "confirming_quote": "Conferma preventivo",
        }
        await update.message.reply_text(
            MSG_STATE_ACTIVE.format(
                customer_name=state_data.get("customer_name", "—"),
                window_count=state_data.get("window_count", 0),
                state=state_labels.get(state, state),
            ),
            parse_mode="Markdown",
        )


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /annulla — reset sessione"""
    if not update.message:
        return

    chat_id = update.effective_chat.id
    session = await SessionManager.get_or_create(chat_id)

    if session is None:
        await update.message.reply_text(MSG_NOT_CONNECTED, parse_mode="Markdown")
        return

    await SessionManager.reset(chat_id)
    await update.message.reply_text(MSG_CANCELLED, parse_mode="Markdown")
