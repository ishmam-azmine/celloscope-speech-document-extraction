from app.adapters.ocr.base import OCRProvider
from app.adapters.ocr.gemini import GeminiOCRProvider
from app.adapters.ocr.mock import MockOCRProvider
from app.config import Settings


def get_ocr_provider(settings: Settings) -> OCRProvider:
    if settings.ocr_provider == "mock":
        return MockOCRProvider(
            response_file="testdata/mock_responses/lab_report_ocr.json"
        )

    if settings.ocr_provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is required when OCR_PROVIDER=gemini."
            )

        return GeminiOCRProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    raise ValueError(
        f"Unsupported OCR provider: {settings.ocr_provider}"
    )