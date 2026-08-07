from app.adapters.transcription.base import TranscriptionProvider
from app.services.models import TranscriptionResult
from app.services.transcription_service import TranscriptionService


class SilentProvider(TranscriptionProvider):
    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        return TranscriptionResult(
            transcript="   ",
            detected_language="en",
            duration_seconds=4.0,
            provider="test",
        )


def test_silence_returns_empty_transcript():
    service = TranscriptionService(provider=SilentProvider())

    result = service.transcribe(
        audio_path="unused.wav",
        language="en",
    )

    assert result.transcript == ""
    assert result.detected_language == "en"
    assert result.duration_seconds == 4.0
    assert result.provider == "test"