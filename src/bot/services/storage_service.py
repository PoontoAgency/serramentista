"""Servizio upload file su Supabase Storage"""
import logging
from uuid import uuid4

from config import settings

try:
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception:
    supabase = None

logger = logging.getLogger(__name__)


class StorageService:
    """Upload file su Supabase Storage"""

    @staticmethod
    async def upload_photo(company_id: str, photo_bytes: bytes, extension: str = "jpg") -> str | None:
        """Upload foto su bucket 'photos', ritorna URL pubblico"""
        return await StorageService._upload(
            bucket="photos",
            path=f"{company_id}/{uuid4().hex}.{extension}",
            file_bytes=photo_bytes,
            mime_type=f"image/{extension}",
        )

    @staticmethod
    async def upload_voice(company_id: str, audio_bytes: bytes) -> str | None:
        """Upload nota vocale su bucket 'voice-notes'"""
        return await StorageService._upload(
            bucket="voice-notes",
            path=f"{company_id}/{uuid4().hex}.ogg",
            file_bytes=audio_bytes,
            mime_type="audio/ogg",
        )

    @staticmethod
    async def _upload(bucket: str, path: str, file_bytes: bytes, mime_type: str) -> str | None:
        """Upload generico su Supabase Storage"""
        if not supabase:
            return None

        try:
            supabase.storage.from_(bucket).upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": mime_type},
            )

            url = supabase.storage.from_(bucket).get_public_url(path)
            logger.info(f"Uploaded to {bucket}/{path}")
            return url

        except Exception as e:
            logger.exception(f"Storage upload error: {e}")
            return None
