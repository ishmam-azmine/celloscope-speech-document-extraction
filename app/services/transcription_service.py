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
        result = self.provider.transcribe(
            audio_path=audio_path,
            language=language,
        )

        transcript = result.transcript.strip()

        if not transcript:
            return TranscriptionResult(
                transcript="",
                detected_language=result.detected_language,
                duration_seconds=result.duration_seconds,
                provider=result.provider,
            )

        return TranscriptionResult(
            transcript=transcript,
            detected_language=result.detected_language,
            duration_seconds=result.duration_seconds,
            provider=result.provider,
        )