from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_extract_lab_report_returns_200():
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.png", b"fake image data", "image/png")},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["meta"]["patient_name"] == "John Doe"
    assert body["meta"]["age"] == "35"
    assert body["meta"]["sex"] == "Male"
    assert body["provider"] == "MockOCRProvider"

    assert len(body["results"]) == 3
    assert body["results"][0]["test_name"] == "Glucose"
    assert body["results"][0]["value"] == 95
    assert body["results"][0]["unit"] == "mg/dL"


def test_preserves_raw_ocr_line():
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.jpg", b"fake image data", "image/jpeg")},
    )

    assert response.status_code == 200

    result = response.json()["results"][0]

    assert result["raw_line"] == "Glucose 95 mg/dL 70-100"


def test_rejects_unsupported_document_type():
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.pdf", b"fake pdf data", "application/pdf")},
    )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "unsupported_document_type"


def test_rejects_empty_document():
    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.png", b"", "image/png")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "empty_document"