from typing import Literal

from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcript: str
    detected_language: Literal["bn", "en"]
    duration_seconds: float
    provider: str


class LabReportMetaResponse(BaseModel):
    patient_name: str | None
    age: str | None
    sex: str | None
    report_date: str | None
    lab_name: str | None
    reference_no: str | None


class LabTestResultResponse(BaseModel):
    test_name: str
    value: float
    unit: str | None
    reference_range: str | None
    flag: str | None
    raw_line: str


class LabReportExtractionResponse(BaseModel):
    meta: LabReportMetaResponse
    results: list[LabTestResultResponse]
    provider: str