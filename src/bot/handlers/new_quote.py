"""Handler /nuovo — inizio nuovo preventivo"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from models.session import SessionState
from services.session_service import SessionManager
from services.customer_service import CustomerService
from services.quote_service import QuoteService
from utils.messages import (
    MSG_NEW_QUOTE_ASK_CUSTOMER, MSG_NEW_QUOTE_CUSTOMER_OK, MSG_NOT_CONNECTED,
)

logger = logging.getLogger(__name__)


async def new_quote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /nuovo — avvia un nuovo preventivo"""
    if not update.message:
        return

    chat_id = update.effective_chat.id
    session = await SessionManager.get_or_create(chat_id)

    if session is None:
        await update.message.reply_text(MSG_NOT_CONNECTED, parse_mode="Markdown")
        return

    # Transizione a AWAITING_CUSTOMER
    await SessionManager.transition(chat_id, SessionState.AWAITING_CUSTOMER)
    await update.message.reply_text(MSG_NEW_QUOTE_ASK_CUSTOMER, parse_mode="Markdown")


async def customer_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce il testo libero quando si è in AWAITING_CUSTOMER"""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    session = await SessionManager.get_or_create(chat_id)

    if not session or session.get("state") != SessionState.AWAITING_CUSTOMER.value:
        return  # Non in stato corretto

    company_id = session.get("company_id")
    text = update.message.text.strip()

    # Trova o crea cliente
    customer = await CustomerService.find_or_create(company_id, text)
    if not customer:
        await update.message.reply_text("⚠️ Errore nel creare il cliente. Riprova.")
        return

    # Crea preventivo bozza
    quote = await QuoteService.create_draft(company_id, customer.get("id"))
    if not quote:
        await update.message.reply_text("⚠️ Errore nel creare il preventivo. Riprova.")
        return

    # Transizione a AWAITING_PHOTO
    await SessionManager.transition(
        chat_id,
        SessionState.AWAITING_PHOTO,
        {
            "current_quote_id": quote["id"],
            "customer_name": customer["name"],
            "window_count": 0,
        },
    )

    # Aggiorna sessione con quote_id linkato
    from config import settings
    try:
        from supabase import create_client
        sb = create_client(settings.supabase_url, settings.supabase_service_key)
        sb.table("bot_sessions") \
            .update({"current_quote_id": quote["id"]}) \
            .eq("telegram_chat_id", chat_id) \
            .execute()
    except Exception:
        pass

    await update.message.reply_text(
        MSG_NEW_QUOTE_CUSTOMER_OK.format(customer_name=customer["name"]),
        parse_mode="Markdown",
    )
