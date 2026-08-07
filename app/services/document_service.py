from app.adapters.ocr.base import OCRProvider
from app.services.models import (
    LabReportExtraction,
    LabReportMeta,
    LabTestResult,
)
from app.services.normalizer import normalize_numeric_value, normalize_unit


class DocumentService:
    def __init__(self, provider: OCRProvider):
        self.provider = provider

    def extract(self, image_path: str) -> LabReportExtraction:
        lines = self.provider.extract_text(image_path)

        meta = self._extract_meta(lines)
        results = self._extract_results(lines)

        return LabReportExtraction(
            meta=meta,
            results=results,
            provider=self.provider.__class__.__name__,
        )

    def _extract_meta(self, lines: list[str]) -> LabReportMeta:
        values = {
            "patient_name": None,
            "age": None,
            "sex": None,
            "report_date": None,
            "lab_name": None,
            "reference_no": None,
        }

        for line in lines:
            lower = line.lower()

            if lower.startswith("patient name:"):
                values["patient_name"] = line.split(":", 1)[1].strip()
            elif lower.startswith("age:"):
                values["age"] = line.split(":", 1)[1].strip()
            elif lower.startswith("sex:"):
                values["sex"] = line.split(":", 1)[1].strip()
            elif lower.startswith("report date:"):
                values["report_date"] = line.split(":", 1)[1].strip()
            elif lower.startswith("lab name:"):
                values["lab_name"] = line.split(":", 1)[1].strip()
            elif lower.startswith("reference no:"):
                values["reference_no"] = line.split(":", 1)[1].strip()

        return LabReportMeta(**values)

    def _extract_results(self, lines: list[str]) -> list[LabTestResult]:
        results = []

        for line in lines:
            parts = line.split()

            if len(parts) < 4:
                continue

            value = normalize_numeric_value(parts[1])

            if value is None:
                continue

            results.append(
                LabTestResult(
                    test_name=parts[0],
                    value=value,
                    unit=normalize_unit(parts[2]),
                    reference_range=parts[3],
                    flag=None,
                    raw_line=line,
                )
            )

        return results