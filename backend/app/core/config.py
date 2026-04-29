from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PD Severity Inference API"
    app_version: str = "1.0.0"
    api_prefix: str = ""
    log_level: str = "INFO"

    model_source: str = Field(default="local", description="local|s3")
    local_model_dir: Path | None = None

    s3_bucket: str | None = None
    s3_prefix: str = "models"
    aws_region: str = "us-east-1"

    model_6m_filename: str = "xgb_sev_6m.joblib"
    model_12m_filename: str = "xgb_sev_12m.joblib"
    model_24m_filename: str = "xgb_sev_24m.joblib"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PD_",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]

if settings.local_model_dir is None:
    settings.local_model_dir = PROJECT_ROOT / "models"
