from typing import Literal

from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcript: str
    detected_language: Literal["bn", "en"]
    duration_seconds: float
    provider: str