from app.adapters.transcription.groq import GroqTranscriptionProvider


def make_provider_without_client() -> GroqTranscriptionProvider:
    return GroqTranscriptionProvider.__new__(GroqTranscriptionProvider)


def test_normalizes_groq_language_names():
    provider = make_provider_without_client()

    assert provider._normalize_language("English", "auto") == "en"
    assert provider._normalize_language("en", "auto") == "en"
    assert provider._normalize_language("Bengali", "auto") == "bn"
    assert provider._normalize_language("Bangla", "auto") == "bn"
    assert provider._normalize_language("bn", "auto") == "bn"


def test_uses_requested_language_when_detection_is_unknown():
    provider = make_provider_without_client()

    assert provider._normalize_language("unknown", "bn") == "bn"
    assert provider._normalize_language("unknown", "en") == "en"