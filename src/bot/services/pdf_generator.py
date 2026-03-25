"""
Servizio generazione PDF preventivo — Jinja2 + WeasyPrint

Genera PDF professionale A4 dal template HTML e lo carica su Supabase Storage.
"""
import logging
import io
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from config import settings

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def format_eur(amount: float) -> str:
    """Formatta importo in EUR: 1234.56 → € 1.234,56"""
    return f"€ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class PDFGenerator:
    """Genera PDF preventivo usando Jinja2 template + WeasyPrint."""

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
        self.env.globals["format_eur"] = format_eur
        self.template = self.env.get_template("quote.html")

    async def build_render_data(self, quote_id: str) -> dict | None:
        """Costruisce i dati per il rendering del template dal database."""
        if not supabase:
            return None

        # Quote con customer e company
        q_result = supabase.table("quotes") \
            .select("*, customers(name, address, city), companies(name, address, city, province, vat_number, phone, email, logo_url)") \
            .eq("id", quote_id) \
            .execute()

        if not q_result.data:
            return None

        quote = q_result.data[0]
        company = quote.get("companies", {}) or {}
        customer = quote.get("customers", {}) or {}

        # Windows
        w_result = supabase.table("windows") \
            .select("*") \
            .eq("quote_id", quote_id) \
            .order("position") \
            .execute()
        windows_raw = w_result.data or []

        windows = []
        total_area = 0
        for w in windows_raw:
            width_mm = float(w.get("width_mm", 0))
            height_mm = float(w.get("height_mm", 0))
            area = float(w.get("area_mq", 0))
            total_area += area
            windows.append({
                "position": w.get("position", 0),
                "window_type": w.get("window_type", "battente"),
                "width_cm": round(width_mm / 10, 1),
                "height_cm": round(height_mm / 10, 1),
                "area_mq": area,
                "notes": w.get("notes", ""),
            })

        # Line items raggruppati per categoria
        items_result = supabase.table("line_items") \
            .select("product_tier, product_name, total_price, products(category_id, product_categories(name))") \
            .eq("quote_id", quote_id) \
            .execute()

        # Raggruppa per categoria
        cat_totals = {}
        tier_subtotals = {"base": 0, "medio": 0, "top": 0}
        for item in (items_result.data or []):
            tier = item.get("product_tier", "base")
            total = float(item.get("total_price", 0))
            tier_subtotals[tier] += total

            # Prova a estrarre il nome categoria
            products_rel = item.get("products", {}) or {}
            cat_rel = products_rel.get("product_categories", {}) or {}
            cat_name = cat_rel.get("name", "Prodotti")

            if cat_name not in cat_totals:
                cat_totals[cat_name] = {"name": cat_name, "total_base": 0, "total_medio": 0, "total_top": 0}
            cat_totals[cat_name][f"total_{tier}"] += total

        product_categories = list(cat_totals.values())

        # Extras
        extras_result = supabase.table("quote_extras") \
            .select("name, quantity, unit, unit_price, total_price") \
            .eq("quote_id", quote_id) \
            .execute()
        extras = extras_result.data or []
        extras_total = sum(float(e.get("total_price", 0)) for e in extras)

        # Totali
        margin_pct = float(quote.get("margin_pct", 25))
        margin_mult = 1 + (margin_pct / 100)

        subtotal_base = tier_subtotals["base"]
        subtotal_medio = tier_subtotals["medio"]
        subtotal_top = tier_subtotals["top"]

        total_base = (subtotal_base + extras_total) * margin_mult
        total_medio = (subtotal_medio + extras_total) * margin_mult
        total_top = (subtotal_top + extras_total) * margin_mult

        margin_base = total_base - subtotal_base - extras_total
        margin_medio = total_medio - subtotal_medio - extras_total
        margin_top = total_top - subtotal_top - extras_total

        # IVA
        iva_pct = 22  # Default Italia

        # Company settings per IVA e validità
        cs_result = supabase.table("company_settings") \
            .select("iva_pct, quote_validity_days") \
            .eq("company_id", quote.get("company_id")) \
            .execute()
        if cs_result.data:
            cs = cs_result.data[0]
            iva_pct = float(cs.get("iva_pct", 22))
            validity_days = int(cs.get("quote_validity_days", 30))
        else:
            validity_days = 30

        iva_mult = 1 + (iva_pct / 100)

        return {
            "company": company,
            "customer": customer,
            "quote": {
                "number": quote.get("number", ""),
                "date": datetime.now().strftime("%d/%m/%Y"),
                "validity_days": validity_days,
            },
            "windows": windows,
            "total_area": total_area,
            "product_categories": product_categories,
            "subtotal_base": subtotal_base,
            "subtotal_medio": subtotal_medio,
            "subtotal_top": subtotal_top,
            "extras": extras,
            "extras_total": extras_total,
            "margin_pct": margin_pct,
            "margin_base": margin_base,
            "margin_medio": margin_medio,
            "margin_top": margin_top,
            "total_base": total_base,
            "total_medio": total_medio,
            "total_top": total_top,
            "total_base_iva": round(total_base * iva_mult, 2),
            "total_medio_iva": round(total_medio * iva_mult, 2),
            "total_top_iva": round(total_top * iva_mult, 2),
            "iva_pct": iva_pct,
            "notes": quote.get("notes", ""),
        }

    async def generate_pdf(self, quote_id: str) -> bytes | None:
        """Genera il PDF come bytes."""
        data = await self.build_render_data(quote_id)
        if not data:
            logger.error(f"Cannot build render data for quote {quote_id}")
            return None

        html = self.template.render(**data)

        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            logger.info(f"PDF generated for quote {quote_id}: {len(pdf_bytes)} bytes")
            return pdf_bytes
        except ImportError:
            logger.warning("WeasyPrint not available, returning HTML as fallback")
            return html.encode("utf-8")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return None

    async def generate_and_upload(self, quote_id: str, company_id: str, number: str) -> str | None:
        """Genera PDF, lo carica su Supabase Storage, aggiorna il record. Ritorna URL."""
        pdf_bytes = await self.generate_pdf(quote_id)
        if not pdf_bytes:
            return None

        if not supabase:
            return None

        # Upload su Supabase Storage
        path = f"{company_id}/{number}.pdf"
        try:
            supabase.storage.from_("pdfs").upload(
                path, pdf_bytes,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
            pdf_url = supabase.storage.from_("pdfs").get_public_url(path)

            # Aggiorna il record quote
            supabase.table("quotes").update({
                "pdf_url": pdf_url,
                "status": "sent",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", quote_id).execute()

            logger.info(f"PDF uploaded: {path} → {pdf_url}")
            return pdf_url
        except Exception as e:
            logger.error(f"PDF upload failed: {e}")
            return None


# Singleton
pdf_generator = PDFGenerator()
