"""Servizio catalogo — lettura prodotti, creazione righe, calcolo totali"""
import logging
from typing import Optional
from decimal import Decimal

from config import settings

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)


class CatalogService:
    """Gestione catalogo prodotti e calcoli preventivo"""

    # ── Lettura catalogo ──────────────────────────────────────

    @staticmethod
    async def get_categories(company_id: str) -> list:
        """Restituisce le categorie attive di un'azienda"""
        if not supabase:
            return []
        result = supabase.table("product_categories") \
            .select("id, name, sort_order") \
            .eq("company_id", company_id) \
            .eq("is_active", True) \
            .order("sort_order") \
            .execute()
        return result.data or []

    @staticmethod
    async def get_products(company_id: str, tier: Optional[str] = None,
                           category_id: Optional[str] = None) -> list:
        """Restituisce i prodotti attivi, con filtro opzionale per tier/categoria"""
        if not supabase:
            return []
        query = supabase.table("products") \
            .select("id, name, sku, supplier, unit, tier, price, category_id, applies_to") \
            .eq("company_id", company_id) \
            .eq("is_active", True)
        if tier:
            query = query.eq("tier", tier)
        if category_id:
            query = query.eq("category_id", category_id)
        result = query.order("name").execute()
        return result.data or []

    @staticmethod
    async def get_products_by_tier(company_id: str) -> dict:
        """Restituisce i prodotti raggruppati per tier: {base: [...], medio: [...], top: [...]}"""
        if not supabase:
            return {"base": [], "medio": [], "top": []}
        all_products = await CatalogService.get_products(company_id)
        grouped = {"base": [], "medio": [], "top": []}
        for p in all_products:
            tier = p.get("tier", "base")
            if tier in grouped:
                grouped[tier].append(p)
        return grouped

    @staticmethod
    async def get_extra_presets(company_id: str) -> list:
        """Restituisce le voci extra preimpostate attive"""
        if not supabase:
            return []
        result = supabase.table("extra_presets") \
            .select("id, name, description, default_price, unit, sort_order") \
            .eq("company_id", company_id) \
            .eq("is_active", True) \
            .order("sort_order") \
            .execute()
        return result.data or []

    # ── Creazione righe preventivo ────────────────────────────

    @staticmethod
    async def create_line_items(quote_id: str, windows: list, products_by_tier: dict) -> list:
        """
        Crea le righe prodotto per ogni finestra × prodotto × tier.
        products_by_tier: {base: [...], medio: [...], top: [...]}
        Ogni prodotto ha: id, name, unit, tier, price, applies_to
        Ogni finestra ha: id, window_type, area_mq, width_mm, height_mm
        """
        if not supabase:
            return []

        rows = []
        for window in windows:
            w_type = window.get("window_type", "battente")
            area_mq = float(window.get("area_mq", 0))
            perimeter_ml = 2 * (float(window.get("width_mm", 0)) + float(window.get("height_mm", 0))) / 1000

            for tier, products in products_by_tier.items():
                for product in products:
                    # Controlla se il prodotto si applica a questo tipo di finestra
                    applies = product.get("applies_to", [])
                    if applies and w_type not in applies:
                        continue

                    unit = product.get("unit", "mq")
                    price = float(product.get("price", 0))

                    # Calcola quantità in base all'unità
                    if unit == "mq":
                        qty = area_mq
                    elif unit == "ml":
                        qty = perimeter_ml
                    else:  # pz
                        qty = 1.0

                    total = round(qty * price, 2)

                    rows.append({
                        "quote_id": quote_id,
                        "window_id": window["id"],
                        "product_id": product["id"],
                        "product_name": product["name"],
                        "product_tier": tier,
                        "product_unit": unit,
                        "quantity": round(qty, 3),
                        "unit_price": price,
                        "total_price": total,
                    })

        if rows:
            result = supabase.table("line_items").insert(rows).execute()
            logger.info(f"Created {len(rows)} line items for quote {quote_id}")
            return result.data or []
        return []

    @staticmethod
    async def create_quote_extras(quote_id: str, selected_extras: list) -> list:
        """
        Crea le voci extra nel preventivo.
        selected_extras: [{preset_id, name, quantity, unit, unit_price}, ...]
        """
        if not supabase:
            return []

        rows = []
        for extra in selected_extras:
            qty = float(extra.get("quantity", 1))
            price = float(extra.get("unit_price", 0))
            rows.append({
                "quote_id": quote_id,
                "preset_id": extra.get("preset_id"),
                "name": extra["name"],
                "quantity": qty,
                "unit": extra.get("unit", "pz"),
                "unit_price": price,
                "total_price": round(qty * price, 2),
            })

        if rows:
            result = supabase.table("quote_extras").insert(rows).execute()
            logger.info(f"Created {len(rows)} extras for quote {quote_id}")
            return result.data or []
        return []

    # ── Calcolo totali ────────────────────────────────────────

    @staticmethod
    async def calculate_and_save_totals(quote_id: str, margin_pct: float) -> dict:
        """
        Calcola subtotali per tier, extras, applica margine, salva su quotes.
        Restituisce: {subtotal_base, subtotal_medio, subtotal_top, extras_total,
                      total_base, total_medio, total_top, margin_pct}
        """
        if not supabase:
            return {}

        # Subtotali per tier dalle line_items
        items_result = supabase.table("line_items") \
            .select("product_tier, total_price") \
            .eq("quote_id", quote_id) \
            .execute()

        subtotals = {"base": 0.0, "medio": 0.0, "top": 0.0}
        for item in (items_result.data or []):
            tier = item.get("product_tier", "base")
            subtotals[tier] += float(item.get("total_price", 0))

        # Totale extras
        extras_result = supabase.table("quote_extras") \
            .select("total_price") \
            .eq("quote_id", quote_id) \
            .execute()
        extras_total = sum(float(e.get("total_price", 0)) for e in (extras_result.data or []))

        # Applica margine
        margin_mult = 1 + (margin_pct / 100)
        totals = {
            "subtotal_base": round(subtotals["base"], 2),
            "subtotal_medio": round(subtotals["medio"], 2),
            "subtotal_top": round(subtotals["top"], 2),
            "extras_total": round(extras_total, 2),
            "margin_pct": margin_pct,
            "total_base": round((subtotals["base"] + extras_total) * margin_mult, 2),
            "total_medio": round((subtotals["medio"] + extras_total) * margin_mult, 2),
            "total_top": round((subtotals["top"] + extras_total) * margin_mult, 2),
        }

        # Salva su quotes
        supabase.table("quotes") \
            .update(totals) \
            .eq("id", quote_id) \
            .execute()

        logger.info(f"Totals saved for quote {quote_id}: base={totals['total_base']}, "
                    f"medio={totals['total_medio']}, top={totals['total_top']}")
        return totals

    @staticmethod
    async def get_quote_summary(quote_id: str) -> dict | None:
        """Restituisce il riepilogo completo del preventivo"""
        if not supabase:
            return None

        quote = supabase.table("quotes") \
            .select("*, customers(name, address, city)") \
            .eq("id", quote_id) \
            .execute()
        if not quote.data:
            return None

        q = quote.data[0]

        windows = supabase.table("windows") \
            .select("*") \
            .eq("quote_id", quote_id) \
            .order("position") \
            .execute()

        extras = supabase.table("quote_extras") \
            .select("*") \
            .eq("quote_id", quote_id) \
            .execute()

        return {
            "quote": q,
            "windows": windows.data or [],
            "extras": extras.data or [],
        }
