from app.services.document_service import DocumentService
from app.services.ports import OCRProvider


class FakeOCRProvider(OCRProvider):
    def extract_text(self, image_path: str) -> list[str]:
        return [
            "Patient Name: Jane Doe",
            "Age: 42",
            "Gender: Female",
            "Total Cholesterol 185 mg/dL 125 - 200",
            "Blood Glucose 126 mg/dL 70-100 High",
            "Creatinine <0.5 mg/dL 0.6 - 1.2",
            "Platelets 1.2 × 10^3 10^3/µL 150-450",
            "This is not a lab result",
        ]


def test_parses_realistic_lab_result_formats():
    service = DocumentService(provider=FakeOCRProvider())

    result = service.extract("unused.png")

    assert result.meta.patient_name == "Jane Doe"
    assert result.meta.age == "42"
    assert result.meta.sex == "Female"

    assert len(result.results) == 4

    cholesterol = result.results[0]
    assert cholesterol.test_name == "Total Cholesterol"
    assert cholesterol.value == 185.0
    assert cholesterol.unit == "mg/dL"
    assert cholesterol.reference_range == "125-200"
    assert cholesterol.raw_line == "Total Cholesterol 185 mg/dL 125 - 200"

    glucose = result.results[1]
    assert glucose.test_name == "Blood Glucose"
    assert glucose.value == 126.0
    assert glucose.flag == "High"

    creatinine = result.results[2]
    assert creatinine.value == 0.5
    assert creatinine.reference_range == "0.6-1.2"

    platelets = result.results[3]
    assert platelets.test_name == "Platelets"
    assert platelets.value == 1200.0
    assert platelets.unit == "10^3/µL"
    assert platelets.reference_range == "150-450"
    assert platelets.raw_line == "Platelets 1.2 × 10^3 10^3/µL 150-450"


def test_preserves_unparsed_lines_verbatim():
    service = DocumentService(provider=FakeOCRProvider())

    result = service.extract("unused.png")

    assert result.unparsed_lines == [
        "This is not a lab result"
    ]