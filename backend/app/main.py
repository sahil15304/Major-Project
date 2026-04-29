import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routes.health import router as health_router
from app.routes.predict import router as predict_router
from app.services.model_service import ModelService
from app.utils.exceptions import (
    ModelNotReadyError,
    model_not_ready_handler,
    unhandled_exception_handler,
)
from app.utils.logging import configure_logging

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(predict_router, prefix=settings.api_prefix)


@app.on_event("startup")
def startup_event() -> None:
    service = ModelService()
    service.load_models()
    app.state.model_service = service
    logger.info("Application startup complete.")


@app.exception_handler(ModelNotReadyError)
async def model_not_ready_exception_handler(request, exc):
    return await model_not_ready_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid input payload", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return await unhandled_exception_handler(request, exc)
