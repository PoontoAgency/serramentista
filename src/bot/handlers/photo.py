"""Handler foto — ricezione foto → upload → AI → risultato con keyboard"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO

from models.session import SessionState
from models.vision import VisionResult, VisionError
from services.session_service import SessionManager
from services.vision import VisionService
from services.storage_service import StorageService
from services.quote_service import QuoteService
from utils.keyboards import confirm_measures_keyboard, fallback_manual_keyboard, next_window_keyboard
from utils.messages import MSG_PHOTO_ANALYZING, MSG_PHOTO_RESULT, MSG_PHOTO_NO_MARKER, MSG_NOT_CONNECTED
from utils.formatters import format_window_type, format_area_mq

logger = logging.getLogger(__name__)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce ricezione foto finestra"""
    if not update.message or not update.message.photo:
        return

    chat_id = update.effective_chat.id
    session = await SessionManager.get_or_create(chat_id)

    if session is None:
        await update.message.reply_text(MSG_NOT_CONNECTED, parse_mode="Markdown")
        return

    if session.get("state") != SessionState.AWAITING_PHOTO.value:
        await update.message.reply_text(
            "📸 Per analizzare una foto, inizia prima un preventivo con /nuovo",
            parse_mode="Markdown",
        )
        return

    # Messaggio di elaborazione
    processing_msg = await update.message.reply_text(MSG_PHOTO_ANALYZING, parse_mode="Markdown")

    # Scarica la foto più grande
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes_io = BytesIO()
    await photo_file.download_to_memory(photo_bytes_io)
    photo_bytes = photo_bytes_io.getvalue()

    # Upload foto su Supabase Storage
    company_id = session.get("company_id")
    photo_url = await StorageService.upload_photo(company_id, photo_bytes)

    # Analisi AI
    result = await VisionService.analyze_photo(photo_bytes)

    if isinstance(result, VisionError):
        await processing_msg.edit_text(
            f"⚠️ {result.message}\n\n_{result.suggestion}_",
            parse_mode="Markdown",
        )
        return

    # Risultato VisionResult
    state_data = session.get("state_data", {})
    window_count = state_data.get("window_count", 0) + 1

    if not result.marker_detected:
        # Marker non rilevato
        await processing_msg.edit_text(MSG_PHOTO_NO_MARKER, parse_mode="Markdown", reply_markup=fallback_manual_keyboard())
        return

    # Salva finestra nel preventivo
    quote_id = state_data.get("current_quote_id")
    if quote_id:
        window = await QuoteService.add_window(
            quote_id=quote_id,
            position=window_count,
            width_mm=result.width_cm * 10,
            height_mm=result.height_cm * 10,
            window_type=result.window_type,
            confidence=result.confidence,
            photo_url=photo_url,
            ai_response=result.raw_response,
        )

    # Aggiorna stato sessione
    await SessionManager.transition(
        chat_id,
        SessionState.CONFIRMING_MEASURES,
        {
            "window_count": window_count,
            "last_vision_result": result.model_dump(),
            "current_window_id": window["id"] if window else None,
        },
    )

    # Mostra risultato
    notes_text = f"\n📝 _{result.notes}_" if result.notes else ""
    text = MSG_PHOTO_RESULT.format(
        window_num=window_count,
        window_type=format_window_type(result.window_type),
        width_cm=f"{result.width_cm:.1f}",
        height_cm=f"{result.height_cm:.1f}",
        area_mq=format_area_mq(result.area_mq),
        confidence=result.confidence.upper(),
        notes=notes_text,
    )

    await processing_msg.edit_text(text, parse_mode="Markdown", reply_markup=confirm_measures_keyboard())


async def measures_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce i callback delle tastiere misure"""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    chat_id = update.effective_chat.id
    data = query.data

    if data == "measures_confirm":
        # Confermato → chiedi se altra finestra
        await SessionManager.transition(chat_id, SessionState.AWAITING_PHOTO)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "✅ Misure confermate!\n\nScatta la foto della prossima finestra o premi il bottone per chiudere.",
            parse_mode="Markdown",
            reply_markup=next_window_keyboard(),
        )

    elif data == "measures_retry":
        # Rifai foto
        await SessionManager.transition(chat_id, SessionState.AWAITING_PHOTO)
        await query.edit_message_text("🔄 OK, scatta un'altra foto della finestra.", parse_mode="Markdown")

    elif data == "measures_edit":
        # Inserisci manualmente
        await query.edit_message_text(
            "✏️ Scrivi le misure nel formato:\n`larghezza x altezza` (in cm)\n\n_Es: 120 x 150_",
            parse_mode="Markdown",
        )

    elif data == "window_add":
        # Altra finestra
        await SessionManager.transition(chat_id, SessionState.AWAITING_PHOTO)
        await query.edit_message_text("📸 Scatta la foto della prossima finestra.", parse_mode="Markdown")

    elif data == "window_done":
        # Chiudi → riepilogo
        session = await SessionManager.get_or_create(chat_id)
        state_data = session.get("state_data", {})
        quote_id = state_data.get("current_quote_id")

        if quote_id:
            windows = await QuoteService.get_windows(quote_id)
            text_lines = []
            total_area = 0.0
            for w in windows:
                area = float(w.get("area_mq", 0))
                total_area += area
                text_lines.append(
                    f"  #{w['position']} {format_window_type(w['window_type'])} — "
                    f"{float(w['width_mm'])/10:.0f}×{float(w['height_mm'])/10:.0f} cm — "
                    f"{format_area_mq(area)}"
                )

            text = f"📋 *Riepilogo finestre:*\n\n" + "\n".join(text_lines) + \
                   f"\n\n*Totale: {len(windows)} finestre — {format_area_mq(total_area)}*" + \
                   f"\n\nPreventivo completato! 🎉\nLa selezione prodotti e il PDF arriveranno nella fase M3-M4."

            await query.edit_message_text(text, parse_mode="Markdown")

        await SessionManager.reset(chat_id)

    elif data == "manual_measures":
        # Inserimento manuale
        await query.edit_message_text(
            "📏 Scrivi le misure nel formato:\n`larghezza x altezza` (in cm)\n\n_Es: 120 x 150_",
            parse_mode="Markdown",
        )
