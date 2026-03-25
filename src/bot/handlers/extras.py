"""
Handler: extras — Selezione voci extra preimpostate.
Flusso: mostra presets → toggle on/off → quantità/prezzo → salva → margine
"""
import structlog
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.session_service import SessionManager
from services.catalog_service import CatalogService
from models.session import SessionState
from utils.formatters import format_currency

log = structlog.get_logger()


async def show_extras_selection(update, context, company_id: str, quote_id: str):
    """Mostra le voci extra preimpostate con toggle on/off."""
    presets = await CatalogService.get_extra_presets(company_id)

    if not presets:
        msg = (
            "ℹ️ *Nessuna voce extra configurata*\n\n"
            "Puoi aggiungerne dalla dashboard → Catalogo → Voci extra.\n\n"
            "Passiamo al margine..."
        )
        await update.effective_message.reply_text(msg, parse_mode="Markdown")
        await SessionManager.transition(update.effective_chat.id, SessionState.ADJUSTING_MARGIN)
        from handlers.margin import show_margin_selection
        await show_margin_selection(update, context, company_id, quote_id)
        return

    # Inizializza stato selezione extras nel state_data
    session = await SessionManager.get_session(update.effective_chat.id)
    state_data = session.get("state_data", {})
    if "selected_extras" not in state_data:
        state_data["selected_extras"] = {}
        await SessionManager.update_state_data(update.effective_chat.id, state_data)

    selected = state_data.get("selected_extras", {})

    keyboard = []
    for preset in presets:
        pid = preset["id"]
        name = preset["name"]
        price = float(preset.get("default_price", 0))
        is_selected = pid in selected

        icon = "✅" if is_selected else "⬜"
        price_str = f" ({format_currency(price)})" if price > 0 else ""
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} {name}{price_str}",
                callback_data=f"extras:toggle:{pid}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("✅ Conferma voci extra", callback_data="extras:confirm"),
        InlineKeyboardButton("⏩ Salta", callback_data="extras:skip"),
    ])

    total_selected = len(selected)
    msg = (
        f"🔧 *Voci extra*\n\n"
        f"Seleziona le voci extra da includere nel preventivo.\n"
        f"Tocca per aggiungere/rimuovere.\n\n"
        f"_Selezionate: {total_selected}_"
    )

    await update.effective_message.reply_text(
        msg, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_extras_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce callback dalla selezione voci extra."""
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
    selected = state_data.get("selected_extras", {})

    if data.startswith("extras:toggle:"):
        preset_id = data.split(":")[2]

        # Toggle: aggiungi/rimuovi dalla selezione
        if preset_id in selected:
            del selected[preset_id]
        else:
            # Carica info preset
            presets = await CatalogService.get_extra_presets(company_id)
            preset = next((p for p in presets if p["id"] == preset_id), None)
            if preset:
                selected[preset_id] = {
                    "preset_id": preset["id"],
                    "name": preset["name"],
                    "quantity": 1,
                    "unit": preset["unit"],
                    "unit_price": float(preset.get("default_price", 0)),
                }

        state_data["selected_extras"] = selected
        await SessionManager.update_state_data(query.message.chat.id, state_data)

        # Refresh keyboard
        presets = await CatalogService.get_extra_presets(company_id)
        keyboard = []
        for preset in presets:
            pid = preset["id"]
            name = preset["name"]
            price = float(preset.get("default_price", 0))
            is_selected = pid in selected
            icon = "✅" if is_selected else "⬜"
            price_str = f" ({format_currency(price)})" if price > 0 else ""
            keyboard.append([
                InlineKeyboardButton(
                    f"{icon} {name}{price_str}",
                    callback_data=f"extras:toggle:{pid}"
                )
            ])
        keyboard.append([
            InlineKeyboardButton("✅ Conferma", callback_data="extras:confirm"),
            InlineKeyboardButton("⏩ Salta", callback_data="extras:skip"),
        ])

        await query.edit_message_text(
            f"🔧 *Voci extra*\n\n"
            f"Tocca per aggiungere/rimuovere.\n\n"
            f"_Selezionate: {len(selected)}_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        log.info("extras.toggled", preset_id=preset_id, selected=len(selected))
        return

    if data == "extras:confirm":
        # Salva le voci extra selezionate
        extras_list = list(selected.values())
        if extras_list:
            await CatalogService.create_quote_extras(quote_id, extras_list)
            extras_total = sum(
                float(e.get("unit_price", 0)) * float(e.get("quantity", 1))
                for e in extras_list
            )
            await query.edit_message_text(
                f"✅ *{len(extras_list)} voci extra aggiunte*\n"
                f"Totale extra: {format_currency(extras_total)}\n\n"
                f"Passiamo al margine...",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "✅ Nessuna voce extra selezionata.\nPassiamo al margine...",
                parse_mode="Markdown"
            )
        log.info("extras.confirmed", quote_id=quote_id, count=len(extras_list))

    elif data == "extras:skip":
        await query.edit_message_text(
            "⏩ Voci extra saltate.\nPassiamo al margine...",
            parse_mode="Markdown"
        )
        log.info("extras.skipped", quote_id=quote_id)

    # Transizione a margine
    await SessionManager.transition(query.message.chat.id, SessionState.ADJUSTING_MARGIN)
    from handlers.margin import show_margin_selection
    await show_margin_selection(update, context, company_id, quote_id)


# Retrocompatibilità
handle_extra_selection = handle_extras_callback
