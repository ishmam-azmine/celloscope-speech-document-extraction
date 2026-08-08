import re

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
from app.services.ports import OCRProvider


class DocumentService:
    def __init__(self, provider: OCRProvider):
        self.provider = provider

    def extract(self, image_path: str) -> LabReportExtraction:
        lines = self.provider.extract_text(image_path)

        meta = self._extract_meta(lines)
        results, unparsed_lines = self._extract_results(lines)

        return LabReportExtraction(
            meta=meta,
            results=results,
            unparsed_lines=unparsed_lines,
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
            "reference_no": (
                r"^(?:reference\s*(?:no|number)|"
                r"ref\s*(?:no|number))\s*:\s*(.+)$"
            ),
        }

        for line in lines:
            stripped = line.strip()

            for field, pattern in field_patterns.items():
                match = re.match(
                    pattern,
                    stripped,
                    flags=re.IGNORECASE,
                )

                if match and values[field] is None:
                    values[field] = match.group(1).strip()

        return LabReportMeta(**values)

    def _extract_results(
        self,
        lines: list[str],
    ) -> tuple[list[LabTestResult], list[str]]:
        results = []
        unparsed_lines = []

        numeric_value = (
            r"[<>≤≥]?\s*"
            r"(?:"
            r"[\d,.]+(?:\.\d+)?"
            r"(?:\s*[x×]\s*10\s*\^?\s*[+-]?\d+)?"
            r")"
        )

        result_pattern = re.compile(
            rf"^(?P<test_name>.+?)\s+"
            rf"(?P<value>{numeric_value})\s+"
            rf"(?P<unit>[^\s]+)\s+"
            rf"(?P<range>[<>≤≥]?\s*[\d,.]+(?:\.\d+)?"
            rf"(?:\s*(?:-|–|—|to)\s*[\d,.]+(?:\.\d+)?)?)"
            rf"(?:\s+(?P<flag>[A-Za-z]+))?$",
            flags=re.IGNORECASE,
        )

        metadata_prefixes = (
            "patient name:",
            "name:",
            "age:",
            "sex:",
            "gender:",
            "report date:",
            "date:",
            "lab name:",
            "laboratory:",
            "reference no:",
            "reference number:",
            "ref no:",
            "ref number:",
        )

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.lower().startswith(metadata_prefixes):
                continue

            match = result_pattern.match(stripped)

            if not match:
                unparsed_lines.append(line)
                continue

            value = normalize_numeric_value(
                match.group("value")
            )

            if value is None:
                unparsed_lines.append(line)
                continue

            results.append(
                LabTestResult(
                    test_name=match.group("test_name").strip(),
                    value=value,
                    unit=normalize_unit(
                        match.group("unit")
                    ),
                    reference_range=normalize_reference_range(
                        match.group("range")
                    ),
                    flag=match.group("flag"),
                    raw_line=line,
                )
            )

        return results, unparsed_lines