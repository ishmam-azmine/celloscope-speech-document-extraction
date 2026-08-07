from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.api.transcription import router as transcription_router
from app.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.include_router(transcription_router)
app.include_router(documents_router)