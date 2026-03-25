"""Handler /start e /connect — collegamento account"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from utils.messages import (
    MSG_START, MSG_CONNECT_OK, MSG_CONNECT_NO_TOKEN,
    MSG_CONNECT_INVALID, MSG_CONNECT_ALREADY, MSG_NOT_CONNECTED,
)

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /start — benvenuto + eventuale /connect"""
    if not update.message:
        return

    # Se c'è un argomento (deep link via /start connect_TOKEN)
    args = context.args
    if args and args[0].startswith("connect_"):
        token = args[0].replace("connect_", "")
        await _connect(update, token)
        return

    await update.message.reply_text(MSG_START, parse_mode="Markdown")


async def connect_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce /connect <token> — collega account Telegram"""
    if not update.message:
        return

    args = context.args
    if not args:
        await update.message.reply_text(MSG_CONNECT_NO_TOKEN, parse_mode="Markdown")
        return

    token = args[0]
    await _connect(update, token)


async def _connect(update: Update, token: str) -> None:
    """Logica comune di collegamento account"""
    chat_id = update.effective_chat.id

    if not supabase:
        await update.message.reply_text("⚠️ Database non configurato.")
        return

    # Verifica se già collegato
    existing = supabase.table("companies") \
        .select("company_name") \
        .eq("telegram_chat_id", chat_id) \
        .execute()

    if existing.data:
        company_name = existing.data[0]["company_name"]
        await update.message.reply_text(
            MSG_CONNECT_ALREADY.format(company_name=company_name),
            parse_mode="Markdown",
        )
        return

    # Cerca azienda con questo token
    result = supabase.table("companies") \
        .select("id, company_name") \
        .eq("telegram_token", token) \
        .execute()

    if not result.data:
        await update.message.reply_text(MSG_CONNECT_INVALID, parse_mode="Markdown")
        return

    company = result.data[0]

    # Collega
    from datetime import datetime, timezone
    supabase.table("companies") \
        .update({
            "telegram_chat_id": chat_id,
            "telegram_linked_at": datetime.now(timezone.utc).isoformat(),
        }) \
        .eq("id", company["id"]) \
        .execute()

    logger.info(f"Company {company['company_name']} linked to chat {chat_id}")
    await update.message.reply_text(
        MSG_CONNECT_OK.format(company_name=company["company_name"]),
        parse_mode="Markdown",
    )
