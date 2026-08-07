from pathlib import Path

from google import genai
from google.genai import types

from app.adapters.ocr.base import OCRProvider


class GeminiOCRProvider(OCRProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
    ):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract_text(self, image_path: str) -> list[str]:
        path = Path(image_path)

        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }

        mime_type = mime_types.get(path.suffix.lower())

        if mime_type is None:
            raise ValueError("Unsupported image type for Gemini OCR.")

        image_bytes = path.read_bytes()

        prompt = (
            "Act only as an OCR system. Transcribe the visible text from this "
            "medical laboratory report image. Preserve the wording, numbers, "
            "units, symbols, and line structure as closely as possible. "
            "Do not interpret, correct, normalize, summarize, or invent text. "
            "Return only the transcribed text, with one OCR line per line."
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
            ],
        )

        text = response.text or ""

        return [
            line
            for line in text.splitlines()
            if line.strip()
        ]