from app.adapters.transcription.factory import get_transcription_provider
from app.adapters.transcription.mock import MockTranscriptionProvider
from app.config import Settings


def test_factory_returns_mock_provider_by_default():
    settings = Settings(
        transcription_provider="mock",
        ocr_provider="mock",
    )

    provider = get_transcription_provider(
        settings=settings,
        language="en",
    )

    assert isinstance(provider, MockTranscriptionProvider)