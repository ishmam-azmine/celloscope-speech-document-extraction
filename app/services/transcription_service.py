from app.adapters.transcription.base import TranscriptionProvider
from app.services.models import TranscriptionResult


class TranscriptionService:
    def __init__(self, provider: TranscriptionProvider):
        self.provider = provider

    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        return self.provider.transcribe(
            audio_path=audio_path,
            language=language,
        )