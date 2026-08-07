import os
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.schemas import TranscriptionResponse
from app.adapters.transcription.mock import MockTranscriptionProvider
from app.config import get_settings
from app.services.transcription_service import TranscriptionService


router = APIRouter(prefix="/api/v1", tags=["Transcription"])

settings = get_settings()

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/x-m4a",
}


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Literal["bn", "en", "auto"] = Form("auto"),
) -> TranscriptionResponse:
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "code": "unsupported_audio_type",
                "message": "Unsupported audio file type.",
            },
        )

    contents = await file.read()

    max_size_bytes = settings.max_audio_size_mb * 1024 * 1024
    if len(contents) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "audio_too_large",
                "message": f"Audio file must not exceed {settings.max_audio_size_mb} MB.",
            },
        )

    suffix = Path(file.filename or "audio").suffix

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        if language == "bn":
            response_file = "testdata/mock_responses/transcription_bn.json"
        else:
            response_file = "testdata/mock_responses/transcription_en.json"

        provider = MockTranscriptionProvider(response_file=response_file)
        service = TranscriptionService(provider=provider)

        result = service.transcribe(
            audio_path=temp_path,
            language=language,
        )

        return TranscriptionResponse(
            transcript=result.transcript,
            detected_language=result.detected_language,
            duration_seconds=result.duration_seconds,
            provider=result.provider,
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)