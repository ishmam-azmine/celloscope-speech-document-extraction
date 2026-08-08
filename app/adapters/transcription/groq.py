from pathlib import Path

from groq import Groq

from app.services.models import TranscriptionResult
from app.services.ports import TranscriptionProvider


class GroqTranscriptionProvider(TranscriptionProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "whisper-large-v3",
    ):
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

        detected_language = self._normalize_language(
            getattr(response, "language", None),
            requested_language=language,
        )

        duration = getattr(response, "duration", 0.0) or 0.0

        return TranscriptionResult(
            transcript=response.text.strip(),
            detected_language=detected_language,
            duration_seconds=float(duration),
            provider="groq",
        )

    def _normalize_language(
        self,
        detected_language: str | None,
        requested_language: str,
    ) -> str:
        if detected_language:
            normalized = detected_language.strip().lower()

            language_map = {
                "en": "en",
                "english": "en",
                "bn": "bn",
                "bengali": "bn",
                "bangla": "bn",
            }

            if normalized in language_map:
                return language_map[normalized]

        if requested_language in {"bn", "en"}:
            return requested_language

        return "en"