"""Servizio trascrizione vocali con OpenAI Whisper"""
import logging
import httpx

from config import settings

logger = logging.getLogger(__name__)


class WhisperService:
    """Trascrizione note vocali via Whisper"""

    @staticmethod
    async def transcribe(audio_bytes: bytes, filename: str = "voice.ogg") -> str | None:
        """Trascrive un file audio → testo"""
        if not settings.openai_api_key:
            logger.error("OpenAI API key non configurata")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    files={"file": (filename, audio_bytes, "audio/ogg")},
                    data={"model": "whisper-1", "language": "it"},
                )

            if response.status_code != 200:
                logger.error(f"Whisper API error: {response.status_code}")
                return None

            text = response.json().get("text", "").strip()
            logger.info(f"Transcribed: {text[:80]}...")
            return text

        except Exception as e:
            logger.exception(f"Whisper service error: {e}")
            return None
