"""Handler note vocali — ricezione → trascrizione → salvataggio"""
import logging
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes

from services.session_service import SessionManager
from services.transcription import WhisperService
from services.storage_service import StorageService
from utils.messages import MSG_VOICE_TRANSCRIBED, MSG_VOICE_ERROR, MSG_NOT_CONNECTED

logger = logging.getLogger(__name__)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gestisce ricezione nota vocale → trascrizione Whisper"""
    if not update.message or not update.message.voice:
        return

    chat_id = update.effective_chat.id
    session = await SessionManager.get_or_create(chat_id)

    if session is None:
        await update.message.reply_text(MSG_NOT_CONNECTED, parse_mode="Markdown")
        return

    # Scarica audio
    voice = update.message.voice
    voice_file = await voice.get_file()
    voice_io = BytesIO()
    await voice_file.download_to_memory(voice_io)
    voice_bytes = voice_io.getvalue()

    # Upload su Storage
    company_id = session.get("company_id")
    voice_url = await StorageService.upload_voice(company_id, voice_bytes)

    # Trascrivi
    text = await WhisperService.transcribe(voice_bytes)

    if text:
        await update.message.reply_text(
            MSG_VOICE_TRANSCRIBED.format(text=text),
            parse_mode="Markdown",
        )

        # Se c'è una finestra corrente, salva la trascrizione
        state_data = session.get("state_data", {})
        window_id = state_data.get("current_window_id")
        if window_id:
            try:
                from config import settings
                from supabase import create_client
                sb = create_client(settings.supabase_url, settings.supabase_service_key)
                sb.table("windows") \
                    .update({"voice_note_url": voice_url, "voice_transcript": text}) \
                    .eq("id", window_id) \
                    .execute()
            except Exception as e:
                logger.error(f"Failed to save voice transcript: {e}")
    else:
        await update.message.reply_text(MSG_VOICE_ERROR, parse_mode="Markdown")
