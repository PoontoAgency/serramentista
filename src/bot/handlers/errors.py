"""
Handler: errors — Gestione errori globale avanzata.

Gestisce errori specifici (OpenAI timeout, Supabase, rate limit)
con messaggi user-friendly differenziati.
"""

import traceback
from datetime import datetime, timezone
from collections import defaultdict

import structlog
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut, NetworkError, BadRequest, Forbidden

log = structlog.get_logger()

# Rate limiting: max 30 messaggi/minuto per utente
_user_message_count: dict[int, list[datetime]] = defaultdict(list)
RATE_LIMIT = 30
RATE_WINDOW_SECONDS = 60


def check_rate_limit(user_id: int) -> bool:
    """Ritorna True se l'utente ha superato il rate limit."""
    now = datetime.now(timezone.utc)
    messages = _user_message_count[user_id]

    # Rimuovi messaggi fuori finestra
    _user_message_count[user_id] = [
        ts for ts in messages
        if (now - ts).total_seconds() < RATE_WINDOW_SECONDS
    ]

    if len(_user_message_count[user_id]) >= RATE_LIMIT:
        return True

    _user_message_count[user_id].append(now)
    return False


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitizza input utente: tronca, rimuove caratteri di controllo."""
    if not text:
        return ""
    # Rimuovi caratteri di controllo (tranne newline e tab)
    cleaned = "".join(
        c for c in text
        if c in ("\n", "\t") or (ord(c) >= 32)
    )
    # Tronca a max_length
    return cleaned[:max_length].strip()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce errori non catturati — logga e invia messaggio user-friendly."""
    error = context.error

    # Classifica l'errore
    if isinstance(error, TimedOut):
        message = (
            "⏱️ La richiesta ha impiegato troppo tempo.\n"
            "Riprova tra qualche secondo."
        )
        log.warning("bot.timeout", error=str(error))
    elif "openai" in str(type(error).__module__).lower() if hasattr(type(error), '__module__') else False:
        message = (
            "🤖 Il servizio AI è temporaneamente sovraccarico.\n"
            "Riprova tra qualche secondo."
        )
        log.error("bot.openai_error", error=str(error))
    elif "supabase" in str(error).lower() or "postgrest" in str(error).lower():
        message = (
            "📊 Il database è temporaneamente non raggiungibile.\n"
            "Riprova tra qualche secondo."
        )
        log.error("bot.supabase_error", error=str(error))
    elif isinstance(error, Forbidden):
        log.warning("bot.forbidden", error=str(error))
        return  # L'utente ha bloccato il bot, non possiamo rispondere
    elif isinstance(error, BadRequest):
        message = (
            "⚠️ Richiesta non valida.\n"
            "Prova un altro tipo di messaggio o usa /annulla."
        )
        log.warning("bot.bad_request", error=str(error))
    elif isinstance(error, NetworkError):
        message = (
            "🌐 Problema di rete temporaneo.\n"
            "Riprova tra qualche secondo."
        )
        log.warning("bot.network_error", error=str(error))
    else:
        message = (
            "⚠️ Si è verificato un errore.\n"
            "Riprova tra qualche secondo.\n\n"
            "Se il problema persiste, usa /annulla e ricomincia."
        )
        log.error(
            "bot.error",
            error=str(error),
            error_type=type(error).__name__,
            traceback=traceback.format_exception(
                None, error, error.__traceback__
            ),
        )

    # Invia messaggio user-friendly se possibile
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(message)
        except Exception:
            pass
