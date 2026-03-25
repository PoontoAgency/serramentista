"""Servizio gestione clienti"""
import logging
from typing import Optional

from config import settings

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)


class CustomerService:
    """CRUD clienti su Supabase"""

    @staticmethod
    async def find_or_create(company_id: str, text: str) -> dict | None:
        """Trova un cliente per nome o ne crea uno nuovo da testo libero.
        
        Il testo può essere:
        - "Mario Rossi" → nome
        - "Mario Rossi, Via Roma 1, Milano" → nome + indirizzo + città
        """
        if not supabase:
            return None

        # Parse testo
        parts = [p.strip() for p in text.split(",")]
        name = parts[0]
        address = parts[1] if len(parts) > 1 else None
        city = parts[2] if len(parts) > 2 else None

        # Cerca cliente esistente per nome (case insensitive)
        result = supabase.table("customers") \
            .select("*") \
            .eq("company_id", company_id) \
            .ilike("name", name) \
            .is_("deleted_at", "null") \
            .execute()

        if result.data:
            logger.info(f"Customer found: {name} ({result.data[0]['id']})")
            return result.data[0]

        # Crea nuovo cliente
        customer = {
            "company_id": company_id,
            "name": name,
            "address": address,
            "city": city,
        }

        result = supabase.table("customers").insert(customer).execute()
        logger.info(f"Customer created: {name}")
        return result.data[0] if result.data else None

    @staticmethod
    async def get_by_id(customer_id: str) -> dict | None:
        """Restituisce un cliente per ID"""
        if not supabase:
            return None

        result = supabase.table("customers") \
            .select("*") \
            .eq("id", customer_id) \
            .execute()
        return result.data[0] if result.data else None
