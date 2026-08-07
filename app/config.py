from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Speech & Document Extraction"
    environment: Literal["development", "test", "production"] = "development"

    transcription_provider: Literal["mock", "groq"] = "mock"
    ocr_provider: str = "mock"

    groq_api_key: str | None = None
    groq_model: str = "whisper-large-v3"

    max_audio_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()