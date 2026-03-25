"""Servizio gestione preventivi"""
import logging
from typing import Optional
from datetime import datetime, timezone

from config import settings

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)


class QuoteService:
    """CRUD preventivi su Supabase"""

    @staticmethod
    async def create_draft(company_id: str, customer_id: Optional[str] = None) -> dict | None:
        """Crea un nuovo preventivo in bozza"""
        if not supabase:
            return None

        # Genera numero progressivo
        year = datetime.now().year
        count_result = supabase.table("quotes") \
            .select("id", count="exact") \
            .eq("company_id", company_id) \
            .eq("year", year) \
            .execute()
        next_num = (count_result.count or 0) + 1

        # Prendi prefisso dalle settings
        settings_result = supabase.table("company_settings") \
            .select("quote_prefix") \
            .eq("company_id", company_id) \
            .execute()
        prefix = settings_result.data[0]["quote_prefix"] if settings_result.data else "SER"

        number = f"{prefix}-{year}-{next_num:04d}"

        quote = {
            "company_id": company_id,
            "customer_id": customer_id,
            "number": number,
            "year": year,
            "status": "draft",
        }

        result = supabase.table("quotes").insert(quote).execute()
        logger.info(f"Quote draft created: {number}")
        return result.data[0] if result.data else None

    @staticmethod
    async def add_window(quote_id: str, position: int, width_mm: float, height_mm: float,
                         window_type: str = "battente", confidence: str = "media",
                         photo_url: Optional[str] = None, ai_response: Optional[dict] = None) -> dict | None:
        """Aggiunge una finestra al preventivo"""
        if not supabase:
            return None

        window = {
            "quote_id": quote_id,
            "position": position,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "window_type": window_type,
            "ai_confidence": confidence,
            "photo_url": photo_url,
            "ai_response_raw": ai_response,
        }

        result = supabase.table("windows").insert(window).execute()
        logger.info(f"Window #{position} added to quote {quote_id}: {width_mm}x{height_mm}mm")
        return result.data[0] if result.data else None

    @staticmethod
    async def get_windows(quote_id: str) -> list:
        """Restituisce tutte le finestre di un preventivo"""
        if not supabase:
            return []

        result = supabase.table("windows") \
            .select("*") \
            .eq("quote_id", quote_id) \
            .order("position") \
            .execute()
        return result.data or []

    @staticmethod
    async def update_status(quote_id: str, status: str) -> None:
        """Aggiorna lo stato del preventivo"""
        if not supabase:
            return

        supabase.table("quotes") \
            .update({"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}) \
            .eq("id", quote_id) \
            .execute()
