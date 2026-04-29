from fastapi import Request
from fastapi.responses import JSONResponse


class ModelNotReadyError(Exception):
    pass


async def model_not_ready_handler(_: Request, exc: ModelNotReadyError):
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc) or "Models are not loaded yet."},
    )


async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )
