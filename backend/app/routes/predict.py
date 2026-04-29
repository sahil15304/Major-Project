from fastapi import APIRouter, Request

from app.models.schemas import PredictionRequest, PredictionResponse

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    model_service = request.app.state.model_service
    result = model_service.predict(
        np1tot=payload.NP1TOT,
        np2tot=payload.NP2TOT,
        np3tot=payload.NP3TOT,
        mcatot=payload.MCATOT,
    )
    return PredictionResponse(**result)
