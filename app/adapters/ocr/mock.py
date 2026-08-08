import json
from pathlib import Path

from app.services.ports import OCRProvider


class MockOCRProvider(OCRProvider):
    def __init__(self, response_file: str):
        self.response_file = Path(response_file)

    def extract_text(self, image_path: str) -> list[str]:
        with self.response_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data["lines"]