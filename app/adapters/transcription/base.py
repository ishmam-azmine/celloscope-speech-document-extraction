from abc import ABC, abstractmethod

from app.services.models import TranscriptionResult


class TranscriptionProvider(ABC):
    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        raise NotImplementedError