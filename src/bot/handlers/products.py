"""
Handler: products — Selezione prodotti dal catalogo per tier.
Flusso: mostra categorie → mostra prodotti per tier → applica a finestre → calcola subtotali
"""
import structlog
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.session_service import SessionManager
from services.catalog_service import CatalogService
from services.quote_service import QuoteService
from models.session import SessionState
from utils.formatters import format_currency

log = structlog.get_logger()


async def show_product_selection(update, context, company_id: str, quote_id: str):
    """Avvia la selezione prodotti — mostra le categorie disponibili."""
    categories = await CatalogService.get_categories(company_id)

    if not categories:
        # Nessun prodotto configurato — salta direttamente a extras
        msg = (
            "⚠️ *Catalogo vuoto*\n\n"
            "Non hai ancora configurato prodotti nella dashboard.\n"
            "Puoi aggiungerli su serramentista.vercel.app → Catalogo.\n\n"
            "Proseguo con le voci extra..."
        )
        await update.effective_message.reply_text(msg, parse_mode="Markdown")
        await SessionManager.transition(update.effective_chat.id, SessionState.SELECTING_EXTRAS)
        from handlers.extras import show_extras_selection
        await show_extras_selection(update, context, company_id, quote_id)
        return

    # Mostra prodotti raggruppati per tier con preview
    products_by_tier = await CatalogService.get_products_by_tier(company_id)
    windows = await QuoteService.get_windows(quote_id)

    # Calcola preview importi per tier
    tier_labels = {"base": "🟢 Base", "medio": "🟡 Medio", "top": "🔴 Top"}
    preview_lines = []

    for tier in ["base", "medio", "top"]:
        products = products_by_tier.get(tier, [])
        if products:
            # Calcola totale stimato per questo tier
            tier_total = 0
            for window in windows:
                area = float(window.get("area_mq", 0))
                perimeter = 2 * (float(window.get("width_mm", 0)) + float(window.get("height_mm", 0))) / 1000
                for p in products:
                    unit = p.get("unit", "mq")
                    price = float(p.get("price", 0))
                    if unit == "mq":
                        tier_total += area * price
                    elif unit == "ml":
                        tier_total += perimeter * price
                    else:
                        tier_total += price
            preview_lines.append(f"{tier_labels[tier]}: {format_currency(tier_total)}")
        else:
            preview_lines.append(f"{tier_labels[tier]}: _nessun prodotto_")

    n_windows = len(windows)
    n_products = sum(len(v) for v in products_by_tier.values())

    msg = (
        f"📦 *Selezione prodotti*\n\n"
        f"Hai {n_products} prodotti in catalogo per {n_windows} finestre.\n\n"
        f"*Stima per fascia:*\n"
        + "\n".join(preview_lines) +
        "\n\n_I prodotti verranno applicati automaticamente in base al tipo di finestra._"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Applica catalogo", callback_data="products:apply_all")],
        [InlineKeyboardButton("🔄 Salta (nessun prodotto)", callback_data="products:skip")],
    ]

    await update.effective_message.reply_text(
        msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce callback dalla selezione prodotti."""
    query = update.callback_query
    await query.answer()
    data = query.data

    session = await SessionManager.get_session(query.message.chat.id)
    if not session:
        await query.edit_message_text("⚠️ Sessione scaduta. Riprova con /nuovo")
        return

    company_id = session.get("company_id")
    quote_id = session.get("current_quote_id")

    if data == "products:apply_all":
        # Applica tutti i prodotti a tutte le finestre
        products_by_tier = await CatalogService.get_products_by_tier(company_id)
        windows = await QuoteService.get_windows(quote_id)

        # Rimuovi eventuali line_items esistenti (in caso di ricalcolo)
        if supabase:
            from config import settings as _s
            from supabase import create_client
            sb = create_client(_s.supabase_url, _s.supabase_service_key)
            sb.table("line_items").delete().eq("quote_id", quote_id).execute()

        line_items = await CatalogService.create_line_items(quote_id, windows, products_by_tier)

        await query.edit_message_text(
            f"✅ *Prodotti applicati!*\n\n"
            f"Creati {len(line_items)} righe per {len(windows)} finestre.\n\n"
            f"Passiamo alle voci extra...",
            parse_mode="Markdown"
        )
        log.info("products.applied", quote_id=quote_id, line_items=len(line_items))

    elif data == "products:skip":
        await query.edit_message_text(
            "⏩ Prodotti saltati.\nPassiamo alle voci extra...",
            parse_mode="Markdown"
        )
        log.info("products.skipped", quote_id=quote_id)

    # Transizione a extras
    await SessionManager.transition(query.message.chat.id, SessionState.SELECTING_EXTRAS)
    from handlers.extras import show_extras_selection
    await show_extras_selection(update, context, company_id, quote_id)


# Retrocompatibilità con lo stub precedente
handle_product_selection = handle_product_callback
