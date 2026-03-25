"""
Handler: margin — Regolazione margine percentuale.
Flusso: mostra margine default → keyboard presets → personalizza → riepilogo → conferma
"""
import structlog
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.session_service import SessionManager
from services.catalog_service import CatalogService
from models.session import SessionState
from utils.formatters import format_currency

log = structlog.get_logger()

MARGIN_PRESETS = [20, 25, 30, 35, 40]


async def show_margin_selection(update, context, company_id: str, quote_id: str):
    """Mostra la selezione margine con preset e opzione personalizzata."""
    # Carica margine default dalle impostazioni azienda
    session = await SessionManager.get_session(update.effective_chat.id)
    state_data = session.get("state_data", {})
    current_margin = state_data.get("margin_pct", 25.0)

    keyboard = []
    row = []
    for pct in MARGIN_PRESETS:
        icon = "✅" if pct == current_margin else ""
        row.append(InlineKeyboardButton(
            f"{icon}{pct}%",
            callback_data=f"margin:set:{pct}"
        ))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("✏️ Personalizza", callback_data="margin:custom"),
    ])
    keyboard.append([
        InlineKeyboardButton("✅ Conferma margine", callback_data="margin:confirm"),
    ])

    msg = (
        f"💰 *Margine di profitto*\n\n"
        f"Margine attuale: *{current_margin:.0f}%*\n\n"
        f"Scegli il margine da applicare al preventivo.\n"
        f"_Il margine viene applicato al subtotale prodotti + extra._"
    )

    await update.effective_message.reply_text(
        msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_margin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce callback dalla selezione margine."""
    query = update.callback_query
    await query.answer()
    data = query.data

    session = await SessionManager.get_session(query.message.chat.id)
    if not session:
        await query.edit_message_text("⚠️ Sessione scaduta. Riprova con /nuovo")
        return

    company_id = session.get("company_id")
    quote_id = session.get("current_quote_id")
    state_data = session.get("state_data", {})

    if data.startswith("margin:set:"):
        pct = float(data.split(":")[2])
        state_data["margin_pct"] = pct
        await SessionManager.update_state_data(query.message.chat.id, state_data)

        # Ricalcola e mostra preview
        totals = await CatalogService.calculate_and_save_totals(quote_id, pct)

        keyboard = []
        row = []
        for preset in MARGIN_PRESETS:
            icon = "✅" if preset == pct else ""
            row.append(InlineKeyboardButton(
                f"{icon}{preset}%",
                callback_data=f"margin:set:{preset}"
            ))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("✏️ Personalizza", callback_data="margin:custom")])
        keyboard.append([InlineKeyboardButton("✅ Conferma margine", callback_data="margin:confirm")])

        msg = (
            f"💰 *Margine: {pct:.0f}%*\n\n"
            f"*Totali stimati:*\n"
            f"🟢 Base: {format_currency(totals.get('total_base', 0))}\n"
            f"🟡 Medio: {format_currency(totals.get('total_medio', 0))}\n"
            f"🔴 Top: {format_currency(totals.get('total_top', 0))}\n"
        )

        await query.edit_message_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        log.info("margin.set", quote_id=quote_id, margin=pct)
        return

    if data == "margin:custom":
        state_data["awaiting_custom_margin"] = True
        await SessionManager.update_state_data(query.message.chat.id, state_data)
        await query.edit_message_text(
            "✏️ *Margine personalizzato*\n\n"
            "Scrivi il margine in percentuale (es: `32` per 32%).",
            parse_mode="Markdown"
        )
        log.info("margin.custom_requested", quote_id=quote_id)
        return

    if data == "margin:confirm":
        margin_pct = state_data.get("margin_pct", 25.0)
        totals = await CatalogService.calculate_and_save_totals(quote_id, margin_pct)

        await query.edit_message_text(
            f"✅ *Margine confermato: {margin_pct:.0f}%*\n\n"
            f"Preparo il riepilogo finale...",
            parse_mode="Markdown"
        )
        log.info("margin.confirmed", quote_id=quote_id, margin=margin_pct)

        # Transizione a conferma
        await SessionManager.transition(query.message.chat.id, SessionState.CONFIRMING_QUOTE)
        from handlers.confirm import show_quote_summary
        await show_quote_summary(update, context, company_id, quote_id)
        return


async def handle_margin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce input testuale per margine personalizzato."""
    session = await SessionManager.get_session(update.effective_chat.id)
    if not session:
        return

    state_data = session.get("state_data", {})
    if not state_data.get("awaiting_custom_margin"):
        return

    text = update.message.text.strip().replace("%", "").replace(",", ".")
    try:
        pct = float(text)
        if pct < 0 or pct > 100:
            await update.message.reply_text("⚠️ Il margine deve essere tra 0% e 100%.")
            return
    except ValueError:
        await update.message.reply_text("⚠️ Inserisci un numero valido (es: 32).")
        return

    company_id = session.get("company_id")
    quote_id = session.get("current_quote_id")
    state_data["margin_pct"] = pct
    state_data["awaiting_custom_margin"] = False
    await SessionManager.update_state_data(update.effective_chat.id, state_data)

    totals = await CatalogService.calculate_and_save_totals(quote_id, pct)

    keyboard = [
        [InlineKeyboardButton("✅ Conferma margine", callback_data="margin:confirm")],
        [InlineKeyboardButton("✏️ Cambia margine", callback_data="margin:custom")],
    ]

    await update.message.reply_text(
        f"💰 *Margine impostato: {pct:.0f}%*\n\n"
        f"🟢 Base: {format_currency(totals.get('total_base', 0))}\n"
        f"🟡 Medio: {format_currency(totals.get('total_medio', 0))}\n"
        f"🔴 Top: {format_currency(totals.get('total_top', 0))}\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    log.info("margin.custom_set", quote_id=quote_id, margin=pct)


# Retrocompatibilità
handle_margin_input = handle_margin_text
