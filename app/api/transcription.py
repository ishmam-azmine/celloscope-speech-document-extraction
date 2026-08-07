import os
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.adapters.transcription.factory import get_transcription_provider
from app.api.schemas import TranscriptionResponse
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

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "empty_audio",
                "message": "Uploaded audio file is empty.",
            },
        )

    max_size_bytes = settings.max_audio_size_mb * 1024 * 1024

    if len(contents) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "audio_too_large",
                "message": (
                    f"Audio file must not exceed "
                    f"{settings.max_audio_size_mb} MB."
                ),
            },
        )

    suffix = Path(file.filename or "audio").suffix
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        try:
            provider = get_transcription_provider(
                settings=settings,
                language=language,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "provider_configuration_error",
                    "message": str(exc),
                },
            ) from exc

        service = TranscriptionService(provider=provider)

        try:
            result = service.transcribe(
                audio_path=temp_path,
                language=language,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "transcription_provider_error",
                    "message": "The transcription provider failed.",
                },
            ) from exc

        return TranscriptionResponse(
            transcript=result.transcript,
            detected_language=result.detected_language,
            duration_seconds=result.duration_seconds,
            provider=result.provider,
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)