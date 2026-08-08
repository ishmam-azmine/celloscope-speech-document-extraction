from fastapi.testclient import TestClient

from app.adapters.transcription.mock import MockTranscriptionProvider
from app.main import app


client = TestClient(app)


def test_no_speech_returns_empty_transcript(monkeypatch):
    provider = MockTranscriptionProvider(
        response_file=(
            "testdata/mock_responses/"
            "transcription_no_speech.json"
        )
    )

    monkeypatch.setattr(
        "app.api.transcription.get_transcription_provider",
        lambda settings, language: provider,
    )

    response = client.post(
        "/api/v1/transcribe",
        files={
            "file": (
                "no_speech_sample.m4a",
                b"fake audio data",
                "audio/x-m4a",
            )
        },
        data={"language": "auto"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["transcript"] == ""
    assert body["provider"] == "mock"