from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_non_lab_document_returns_422(monkeypatch):
    class NonLabProvider:
        def extract_text(self, image_path: str) -> list[str]:
            return [
                "Shopping List",
                "Milk",
                "Bread",
                "Eggs",
            ]

    monkeypatch.setattr(
        "app.api.documents.get_ocr_provider",
        lambda settings: NonLabProvider(),
    )

    response = client.post(
        "/api/v1/documents/extract",
        files={
            "file": (
                "not_a_lab_report.png",
                b"fake image data",
                "image/png",
            )
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"]["code"] == "no_lab_results_found"
    assert body["detail"]["unparsed_lines"] == [
        "Shopping List",
        "Milk",
        "Bread",
        "Eggs",
    ]