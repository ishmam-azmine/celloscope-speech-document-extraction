from fastapi.testclient import TestClient

from app.main import app
from app.services.models import TranscriptionResult


client = TestClient(app)


class FailingProvider:
    def transcribe(
        self,
        audio_path: str,
        language: str,
    ) -> TranscriptionResult:
        raise RuntimeError("Provider unavailable")


def test_transcription_provider_failure_returns_502(monkeypatch):
    monkeypatch.setattr(
        "app.api.transcription.get_transcription_provider",
        lambda settings, language: FailingProvider(),
    )

    response = client.post(
        "/api/v1/transcribe",
        files={
            "file": (
                "sample.wav",
                b"fake audio data",
                "audio/wav",
            )
        },
        data={"language": "en"},
    )

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "transcription_provider_error"