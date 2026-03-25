"""Gestione sessioni bot — persistite su Supabase"""
import logging
from datetime import datetime, timezone
from typing import Optional

from config import settings
from models.session import SessionState, StateData

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)


class SessionManager:
    """Gestisce le sessioni bot persistite su Supabase"""

    @staticmethod
    async def get_or_create(chat_id: int) -> dict:
        """Ottiene la sessione corrente o ne crea una nuova"""
        if not supabase:
            return {"state": SessionState.IDLE.value, "state_data": {}, "telegram_chat_id": chat_id}

        # Cerca sessione attiva
        result = supabase.table("bot_sessions") \
            .select("*") \
            .eq("telegram_chat_id", chat_id) \
            .execute()

        if result.data:
            session = result.data[0]
            # Controlla timeout
            last_activity = datetime.fromisoformat(session["last_activity_at"].replace("Z", "+00:00"))
            if (datetime.now(timezone.utc) - last_activity).total_seconds() > 7200:
                # Sessione scaduta → reset
                logger.info(f"Session expired for chat {chat_id}, resetting")
                await SessionManager.reset(chat_id)
                return await SessionManager.get_or_create(chat_id)
            return session

        # Cerca company collegata a questo chat_id
        company = supabase.table("companies") \
            .select("id") \
            .eq("telegram_chat_id", chat_id) \
            .execute()

        if not company.data:
            return None  # Nessuna azienda collegata

        # Crea nuova sessione
        new_session = {
            "company_id": company.data[0]["id"],
            "telegram_chat_id": chat_id,
            "state": SessionState.IDLE.value,
            "state_data": {},
        }
        result = supabase.table("bot_sessions").insert(new_session).execute()
        return result.data[0] if result.data else new_session

    @staticmethod
    async def transition(chat_id: int, new_state: SessionState, state_data_updates: Optional[dict] = None) -> dict:
        """Transizione di stato della sessione"""
        if not supabase:
            return {"state": new_state.value}

        session = await SessionManager.get_or_create(chat_id)
        if not session or not session.get("id"):
            return session

        current_data = session.get("state_data", {})
        if state_data_updates:
            current_data.update(state_data_updates)

        update = {
            "state": new_state.value,
            "state_data": current_data,
            "last_activity_at": datetime.now(timezone.utc).isoformat(),
        }

        result = supabase.table("bot_sessions") \
            .update(update) \
            .eq("telegram_chat_id", chat_id) \
            .execute()

        logger.info(f"Session {chat_id}: {session.get('state')} → {new_state.value}")
        return result.data[0] if result.data else {**session, **update}

    @staticmethod
    async def reset(chat_id: int) -> None:
        """Reset sessione a IDLE"""
        if not supabase:
            return

        supabase.table("bot_sessions") \
            .update({
                "state": SessionState.IDLE.value,
                "state_data": {},
                "current_quote_id": None,
                "last_activity_at": datetime.now(timezone.utc).isoformat(),
            }) \
            .eq("telegram_chat_id", chat_id) \
            .execute()

        logger.info(f"Session {chat_id}: RESET to IDLE")

    @staticmethod
    async def update_activity(chat_id: int) -> None:
        """Aggiorna il timestamp di ultima attività"""
        if not supabase:
            return

        supabase.table("bot_sessions") \
            .update({"last_activity_at": datetime.now(timezone.utc).isoformat()}) \
            .eq("telegram_chat_id", chat_id) \
            .execute()

    @staticmethod
    async def get_session(chat_id: int) -> Optional[dict]:
        """Alias per get_or_create — restituisce la sessione corrente"""
        return await SessionManager.get_or_create(chat_id)

    @staticmethod
    async def update_state_data(chat_id: int, state_data: dict) -> None:
        """Aggiorna solo lo state_data della sessione"""
        if not supabase:
            return

        supabase.table("bot_sessions") \
            .update({
                "state_data": state_data,
                "last_activity_at": datetime.now(timezone.utc).isoformat(),
            }) \
            .eq("telegram_chat_id", chat_id) \
            .execute()

