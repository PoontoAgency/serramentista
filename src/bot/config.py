"""
Serramentista Bot — Configuration
Carica variabili ambiente con pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram
    telegram_bot_token: str
    bot_mode: str = "polling"  # "polling" in dev, "webhook" in prod
    webhook_url: str = ""

    # OpenAI
    openai_api_key: str

    # Supabase
    supabase_url: str
    supabase_service_key: str  # service_role key (bypassa RLS)

    # App
    log_level: str = "INFO"
    marker_size_mm: int = 210  # A4 width in mm

    # Vision
    vision_model: str = "gpt-4o"
    vision_max_tokens: int = 400
    vision_temperature: float = 0.1
    vision_timeout_seconds: int = 30
    vision_max_retries: int = 2

    # Whisper
    whisper_model: str = "whisper-1"
    whisper_language: str = "it"
    whisper_max_duration: int = 120  # secondi


settings = Settings()
