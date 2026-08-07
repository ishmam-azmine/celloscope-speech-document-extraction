from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TranscriptionResult:
    transcript: str
    detected_language: Literal["bn", "en"]
    duration_seconds: float
    provider: str