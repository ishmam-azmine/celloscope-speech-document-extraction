from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class TranscriptionResult:
    transcript: str
    detected_language: Literal["bn", "en"]
    duration_seconds: float
    provider: str


@dataclass(frozen=True)
class LabReportMeta:
    patient_name: str | None
    age: str | None
    sex: str | None
    report_date: str | None
    lab_name: str | None
    reference_no: str | None


@dataclass(frozen=True)
class LabTestResult:
    test_name: str
    value: float
    unit: str | None
    reference_range: str | None
    flag: str | None
    raw_line: str


@dataclass(frozen=True)
class LabReportExtraction:
    meta: LabReportMeta
    results: list[LabTestResult]
    unparsed_lines: list[str]
    provider: str