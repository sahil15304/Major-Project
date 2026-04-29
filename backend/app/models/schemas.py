from math import isfinite

from pydantic import BaseModel, Field, model_validator


class PredictionRequest(BaseModel):
    NP1TOT: float = Field(..., ge=0, le=52, description="UPDRS Part I total")
    NP2TOT: float = Field(..., ge=0, le=52, description="UPDRS Part II total")
    NP3TOT: float = Field(..., ge=0, le=132, description="UPDRS Part III total")
    MCATOT: float = Field(..., ge=0, le=30, description="MoCA total score")

    @model_validator(mode="after")
    def validate_finite_values(self):
        for key, value in self.model_dump().items():
            if not isfinite(value):
                raise ValueError(f"{key} must be a finite number")
        return self


class PredictionResponse(BaseModel):
    severity_6m: float
    severity_12m: float
    severity_24m: float


class HealthResponse(BaseModel):
    status: str
    model_source: str
    models_loaded: bool
