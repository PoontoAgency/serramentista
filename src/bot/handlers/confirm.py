"""
Handler: confirm — Riepilogo finale e conferma preventivo.
Flusso: riepilogo strutturato → [Genera PDF] / [Modifica margine] / [Modifica extra]
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


async def show_quote_summary(update, context, company_id: str, quote_id: str):
    """Mostra il riepilogo completo del preventivo."""
    summary = await CatalogService.get_quote_summary(quote_id)
    if not summary:
        await update.effective_message.reply_text("⚠️ Errore nel caricamento del preventivo.")
        return

    quote = summary["quote"]
    windows = summary["windows"]
    extras = summary["extras"]

    # Header
    customer_name = "N/D"
    if quote.get("customers"):
        customer_name = quote["customers"].get("name", "N/D")

    lines = [
        f"📋 *Riepilogo preventivo {quote.get('number', '')}*",
        f"👤 Cliente: {customer_name}",
        f"🪟 Finestre: {len(windows)}",
        "",
    ]

    # Finestre
    total_area = 0
    for w in windows:
        width_cm = float(w.get("width_mm", 0)) / 10
        height_cm = float(w.get("height_mm", 0)) / 10
        area = float(w.get("area_mq", 0))
        total_area += area
        w_type = w.get("window_type", "battente")
        lines.append(f"  #{w['position']} {w_type} — {width_cm:.0f}×{height_cm:.0f}cm ({area:.2f}m²)")

    lines.append(f"\n*Area totale: {total_area:.2f} m²*")

    # Extras
    if extras:
        lines.append(f"\n🔧 *Voci extra ({len(extras)}):*")
        for e in extras:
            lines.append(f"  • {e['name']}: {format_currency(float(e.get('total_price', 0)))}")

    # Totali
    margin_pct = float(quote.get("margin_pct", 25))
    extras_total = float(quote.get("extras_total", 0))

    lines.extend([
        "",
        f"💰 *Margine: {margin_pct:.0f}%*",
        f"🔧 Extra: {format_currency(extras_total)}",
        "",
        f"*Totali (IVA esclusa):*",
        f"🟢 Base: *{format_currency(float(quote.get('total_base', 0)))}*",
        f"🟡 Medio: *{format_currency(float(quote.get('total_medio', 0)))}*",
        f"🔴 Top: *{format_currency(float(quote.get('total_top', 0)))}*",
    ])

    keyboard = [
        [InlineKeyboardButton("📄 Genera PDF", callback_data="confirm:generate_pdf")],
        [
            InlineKeyboardButton("✏️ Margine", callback_data="confirm:edit_margin"),
            InlineKeyboardButton("✏️ Extra", callback_data="confirm:edit_extras"),
        ],
        [InlineKeyboardButton("❌ Annulla preventivo", callback_data="confirm:cancel")],
    ]

    await update.effective_message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce callback dal riepilogo preventivo."""
    query = update.callback_query
    await query.answer()
    data = query.data

    session = await SessionManager.get_session(query.message.chat.id)
    if not session:
        await query.edit_message_text("⚠️ Sessione scaduta. Riprova con /nuovo")
        return

    company_id = session.get("company_id")
    quote_id = session.get("current_quote_id")

    if data == "confirm:generate_pdf":
        # M4: qui verrà chiamato il pdf_generator
        # Per ora: segna come 'ready' e torna a idle
        await QuoteService.update_status(quote_id, "ready")
        await SessionManager.transition(query.message.chat.id, SessionState.IDLE)

        await query.edit_message_text(
            "✅ *Preventivo confermato!*\n\n"
            f"Il preventivo è stato salvato con stato *pronto*.\n"
            "La generazione PDF sarà disponibile nella prossima versione.\n\n"
            "Scrivi /nuovo per creare un altro preventivo.",
            parse_mode="Markdown"
        )
        log.info("confirm.pdf_requested", quote_id=quote_id)
        return

    if data == "confirm:edit_margin":
        await SessionManager.transition(query.message.chat.id, SessionState.ADJUSTING_MARGIN)
        await query.edit_message_text("💰 Modifica margine...")
        from handlers.margin import show_margin_selection
        await show_margin_selection(update, context, company_id, quote_id)
        log.info("confirm.edit_margin", quote_id=quote_id)
        return

    if data == "confirm:edit_extras":
        await SessionManager.transition(query.message.chat.id, SessionState.SELECTING_EXTRAS)
        await query.edit_message_text("🔧 Modifica voci extra...")
        from handlers.extras import show_extras_selection
        await show_extras_selection(update, context, company_id, quote_id)
        log.info("confirm.edit_extras", quote_id=quote_id)
        return

    if data == "confirm:cancel":
        await QuoteService.update_status(quote_id, "draft")
        await SessionManager.transition(query.message.chat.id, SessionState.IDLE)
        await query.edit_message_text(
            "❌ *Preventivo annullato.*\n"
            "La bozza resta salvata nel database.\n\n"
            "Scrivi /nuovo per iniziarne uno nuovo.",
            parse_mode="Markdown"
        )
        log.info("confirm.cancelled", quote_id=quote_id)
        return


# Retrocompatibilità
handle_confirm = handle_confirm_callback
