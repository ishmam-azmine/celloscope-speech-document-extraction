from typing import Protocol

from app.services.models import TranscriptionResult


class TranscriptionProvider(Protocol):
    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        ...


class OCRProvider(Protocol):
    def extract_text(
        self,
        image_path: str,
    ) -> list[str]:
        ...