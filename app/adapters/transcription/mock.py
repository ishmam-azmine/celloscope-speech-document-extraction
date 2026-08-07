import json
from pathlib import Path

from app.adapters.transcription.base import TranscriptionProvider
from app.services.models import TranscriptionResult


class MockTranscriptionProvider(TranscriptionProvider):
    def __init__(self, response_file: str):
        self.response_file = Path(response_file)

    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        with self.response_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return TranscriptionResult(
            transcript=data["transcript"],
            detected_language=data["detected_language"],
            duration_seconds=float(data["duration_seconds"]),
            provider="mock",
        )