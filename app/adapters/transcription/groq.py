from pathlib import Path

from groq import Groq

from app.adapters.transcription.base import TranscriptionProvider
from app.services.models import TranscriptionResult


class GroqTranscriptionProvider(TranscriptionProvider):
    def __init__(self, api_key: str, model: str = "whisper-large-v3"):
        self.client = Groq(api_key=api_key)
        self.model = model

    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        path = Path(audio_path)

        with path.open("rb") as audio_file:
            kwargs = {
                "file": (path.name, audio_file.read()),
                "model": self.model,
                "response_format": "verbose_json",
                "temperature": 0.0,
            }

            if language in {"bn", "en"}:
                kwargs["language"] = language

            response = self.client.audio.transcriptions.create(**kwargs)

        detected_language = getattr(response, "language", None)

        if detected_language not in {"bn", "en"}:
            detected_language = language if language in {"bn", "en"} else "en"

        duration = getattr(response, "duration", 0.0) or 0.0

        return TranscriptionResult(
            transcript=response.text.strip(),
            detected_language=detected_language,
            duration_seconds=float(duration),
            provider="groq",
        )