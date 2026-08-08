from app.adapters.transcription.groq import GroqTranscriptionProvider
from app.adapters.transcription.mock import MockTranscriptionProvider
from app.config import Settings
from app.services.ports import TranscriptionProvider


def get_transcription_provider(
    settings: Settings,
    language: str,
) -> TranscriptionProvider:
    if settings.transcription_provider == "mock":
        if language == "bn":
            response_file = "testdata/mock_responses/transcription_bn.json"
        else:
            response_file = "testdata/mock_responses/transcription_en.json"

        return MockTranscriptionProvider(response_file=response_file)

    if settings.transcription_provider == "groq":
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is required when TRANSCRIPTION_PROVIDER=groq."
            )

        return GroqTranscriptionProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        )

    raise ValueError(
        f"Unsupported transcription provider: {settings.transcription_provider}"
    )