from fastapi import APIRouter, Request

from app.core.config import settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    model_service = request.app.state.model_service
    return HealthResponse(
        status="ok",
        model_source=settings.model_source,
        models_loaded=model_service.loaded,
    )
