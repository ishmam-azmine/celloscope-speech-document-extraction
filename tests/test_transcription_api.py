from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_transcribe_english_audio_returns_200():
    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.wav", b"fake audio data", "audio/wav")},
        data={"language": "en"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["transcript"] == "Hello, this is a sample English transcription."
    assert body["detected_language"] == "en"
    assert body["duration_seconds"] == 3.2
    assert body["provider"] == "mock"


def test_transcribe_bengali_audio_returns_200():
    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.wav", b"fake audio data", "audio/wav")},
        data={"language": "bn"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["detected_language"] == "bn"
    assert body["provider"] == "mock"


def test_rejects_unsupported_audio_type():
    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.txt", b"not audio", "text/plain")},
        data={"language": "en"},
    )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "unsupported_audio_type"


def test_rejects_invalid_language():
    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.wav", b"fake audio data", "audio/wav")},
        data={"language": "fr"},
    )

    assert response.status_code == 422