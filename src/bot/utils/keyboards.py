"""Builder per tastiere inline Telegram"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_measures_keyboard() -> InlineKeyboardMarkup:
    """Tastiera per confermare le misure rilevate"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confermo", callback_data="measures_confirm"),
            InlineKeyboardButton("✏️ Correggi", callback_data="measures_edit"),
        ],
        [InlineKeyboardButton("🔄 Rifai foto", callback_data="measures_retry")],
    ])


def next_window_keyboard() -> InlineKeyboardMarkup:
    """Tastiera per aggiungere un'altra finestra o chiudere"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Altra finestra", callback_data="window_add")],
        [InlineKeyboardButton("✅ Chiudi — manda riepilogo", callback_data="window_done")],
    ])


def margin_keyboard() -> InlineKeyboardMarkup:
    """Tastiera per selezionare il margine"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("20%", callback_data="margin_20"),
            InlineKeyboardButton("25%", callback_data="margin_25"),
            InlineKeyboardButton("30%", callback_data="margin_30"),
            InlineKeyboardButton("35%", callback_data="margin_35"),
        ],
        [InlineKeyboardButton("✏️ Personalizza", callback_data="margin_custom")],
    ])


def confirm_quote_keyboard() -> InlineKeyboardMarkup:
    """Tastiera per confermare il preventivo finale"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Genera PDF", callback_data="quote_generate_pdf")],
        [
            InlineKeyboardButton("✏️ Margine", callback_data="quote_edit_margin"),
            InlineKeyboardButton("✏️ Extra", callback_data="quote_edit_extras"),
        ],
        [InlineKeyboardButton("❌ Annulla", callback_data="quote_cancel")],
    ])


def fallback_manual_keyboard() -> InlineKeyboardMarkup:
    """Tastiera per inserimento manuale misure quando il marker non è rilevato"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📏 Inserisci manualmente", callback_data="manual_measures")],
        [InlineKeyboardButton("🔄 Rifai foto con marker", callback_data="measures_retry")],
    ])
