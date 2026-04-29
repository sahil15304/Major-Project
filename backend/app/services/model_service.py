import logging
from pathlib import Path

import joblib
import numpy as np

from app.core.config import settings
from app.utils.exceptions import ModelNotReadyError

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self) -> None:
        self.model_6m = None
        self.model_12m = None
        self.model_24m = None
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded

    def load_models(self) -> None:
        if self._loaded:
            logger.info("Models already loaded. Skipping reload.")
            return

        model_source = settings.model_source.lower()
        logger.info("Loading models using source=%s", model_source)

        if model_source == "s3":
            model_dir = self._download_models_from_s3()
        else:
            model_dir = Path(settings.local_model_dir)

        self.model_6m = self._load_single_model(model_dir / settings.model_6m_filename)
        self.model_12m = self._load_single_model(model_dir / settings.model_12m_filename)
        self.model_24m = self._load_single_model(model_dir / settings.model_24m_filename)

        self._loaded = True
        logger.info("All models loaded successfully.")

    def predict(self, np1tot: float, np2tot: float, np3tot: float, mcatot: float) -> dict:
        if not self._loaded:
            raise ModelNotReadyError("Models are not loaded. Please try again shortly.")

        features = np.array([[np1tot, np2tot, np3tot, mcatot]], dtype=float)

        severity_6m = float(self.model_6m.predict(features)[0])
        severity_12m = float(self.model_12m.predict(features)[0])
        severity_24m = float(self.model_24m.predict(features)[0])

        return {
            "severity_6m": severity_6m,
            "severity_12m": severity_12m,
            "severity_24m": severity_24m,
        }

    @staticmethod
    def _load_single_model(model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        logger.info("Loading model: %s", model_path)
        return joblib.load(model_path)

    @staticmethod
    def _download_models_from_s3() -> Path:
        if not settings.s3_bucket:
            raise ValueError("PD_S3_BUCKET must be set when PD_MODEL_SOURCE=s3")

        import boto3

        s3_client = boto3.client("s3", region_name=settings.aws_region)
        target_dir = Path("/tmp/pd_models")
        target_dir.mkdir(parents=True, exist_ok=True)

        filenames = [
            settings.model_6m_filename,
            settings.model_12m_filename,
            settings.model_24m_filename,
        ]

        for filename in filenames:
            key = f"{settings.s3_prefix.strip('/')}/{filename}"
            destination = target_dir / filename
            logger.info("Downloading s3://%s/%s -> %s", settings.s3_bucket, key, destination)
            s3_client.download_file(settings.s3_bucket, key, str(destination))

        return target_dir
