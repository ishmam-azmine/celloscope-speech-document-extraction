from app.adapters.ocr.factory import get_ocr_provider
from app.adapters.ocr.mock import MockOCRProvider
from app.config import Settings


def test_factory_returns_mock_ocr_provider_by_default():
    settings = Settings(
        transcription_provider="mock",
        ocr_provider="mock",
    )

    provider = get_ocr_provider(settings=settings)

    assert isinstance(provider, MockOCRProvider)