import re

from app.adapters.ocr.base import OCRProvider
from app.services.models import (
    LabReportExtraction,
    LabReportMeta,
    LabTestResult,
)
from app.services.normalizer import (
    normalize_numeric_value,
    normalize_reference_range,
    normalize_unit,
)


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

        field_patterns = {
            "patient_name": r"^(?:patient\s*)?name\s*:\s*(.+)$",
            "age": r"^age\s*:\s*(.+)$",
            "sex": r"^(?:sex|gender)\s*:\s*(.+)$",
            "report_date": r"^(?:report\s*date|date)\s*:\s*(.+)$",
            "lab_name": r"^(?:lab\s*name|laboratory)\s*:\s*(.+)$",
            "reference_no": r"^(?:reference\s*(?:no|number)|ref\s*(?:no|number))\s*:\s*(.+)$",
        }

        for line in lines:
            stripped = line.strip()

            for field, pattern in field_patterns.items():
                match = re.match(pattern, stripped, flags=re.IGNORECASE)

                if match and values[field] is None:
                    values[field] = match.group(1).strip()

        return LabReportMeta(**values)

    def _extract_results(self, lines: list[str]) -> list[LabTestResult]:
        results = []

        result_pattern = re.compile(
            r"^(?P<test_name>.+?)\s+"
            r"(?P<value>[<>≤≥]?\s*[\d,.]+(?:\.\d+)?)\s+"
            r"(?P<unit>[^\s]+)\s+"
            r"(?P<range>[<>≤≥]?\s*[\d,.]+(?:\.\d+)?"
            r"(?:\s*(?:-|–|—|to)\s*[\d,.]+(?:\.\d+)?)?)"
            r"(?:\s+(?P<flag>[A-Za-z]+))?$",
            flags=re.IGNORECASE,
        )

        for line in lines:
            match = result_pattern.match(line.strip())

            if not match:
                continue

            value = normalize_numeric_value(match.group("value"))

            if value is None:
                continue

            results.append(
                LabTestResult(
                    test_name=match.group("test_name").strip(),
                    value=value,
                    unit=normalize_unit(match.group("unit")),
                    reference_range=normalize_reference_range(
                        match.group("range")
                    ),
                    flag=match.group("flag"),
                    raw_line=line,
                )
            )

        return results