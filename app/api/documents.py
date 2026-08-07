import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.adapters.ocr.factory import get_ocr_provider
from app.api.schemas import LabReportExtractionResponse
from app.config import get_settings
from app.services.document_service import DocumentService


router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

settings = get_settings()

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


@router.post(
    "/extract",
    response_model=LabReportExtractionResponse,
)
async def extract_document(
    file: UploadFile = File(...),
) -> LabReportExtractionResponse:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "code": "unsupported_document_type",
                "message": "Unsupported document file type.",
            },
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "empty_document",
                "message": "Uploaded document is empty.",
            },
        )

    suffix = Path(file.filename or "document").suffix
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        try:
            provider = get_ocr_provider(settings=settings)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "provider_configuration_error",
                    "message": str(exc),
                },
            ) from exc

        service = DocumentService(provider=provider)
        result = service.extract(image_path=temp_path)

        if not result.results:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "no_lab_results_found",
                    "message": "No valid laboratory results could be extracted.",
                },
            )

        return LabReportExtractionResponse(
            meta={
                "patient_name": result.meta.patient_name,
                "age": result.meta.age,
                "sex": result.meta.sex,
                "report_date": result.meta.report_date,
                "lab_name": result.meta.lab_name,
                "reference_no": result.meta.reference_no,
            },
            results=[
                {
                    "test_name": item.test_name,
                    "value": item.value,
                    "unit": item.unit,
                    "reference_range": item.reference_range,
                    "flag": item.flag,
                    "raw_line": item.raw_line,
                }
                for item in result.results
            ],
            provider=result.provider,
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)