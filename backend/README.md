# Parkinson's Severity Inference Backend (FastAPI)

Production-ready inference API for 3 pre-trained XGBoost models:
- `severity_6m`
- `severity_12m`
- `severity_24m`

Features:
- Loads models once at startup
- Validates input payload with Pydantic
- Predict endpoint + health endpoint
- Structured logging and exception handling
- Supports local model files or S3 model source
- Ready for EC2 and Docker deployment

## 1) Folder Structure

```text
backend/
  app/
    core/
      config.py
    models/
      schemas.py
    routes/
      health.py
      predict.py
    services/
      model_service.py
    utils/
      exceptions.py
      logging.py
    main.py
  .env.example
  Dockerfile
  requirements.txt
  README.md
```

## 2) API Contract

### `POST /predict`
Request:
```json
{
  "NP1TOT": 10.0,
  "NP2TOT": 12.0,
  "NP3TOT": 30.0,
  "MCATOT": 26.0
}
```

Response:
```json
{
  "severity_6m": 0.41,
  "severity_12m": 0.49,
  "severity_24m": 0.57
}
```

### `GET /health`
Response:
```json
{
  "status": "ok",
  "model_source": "local",
  "models_loaded": true
}
```

Swagger docs: `http://localhost:8000/docs`

## 3) Run Locally

From project root (`PPMI_Project`):

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4) Test with curl

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"NP1TOT":10,"NP2TOT":12,"NP3TOT":30,"MCATOT":26}'
```

Health:
```bash
curl "http://localhost:8000/health"
```

## 5) Test with Postman

1. Method: `POST`
2. URL: `http://localhost:8000/predict`
3. Header: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "NP1TOT": 10,
  "NP2TOT": 12,
  "NP3TOT": 30,
  "MCATOT": 26
}
```

## 6) Deploy on AWS EC2

### EC2 steps
1. Launch Ubuntu EC2 instance (t3.small or higher).
2. Open Security Group inbound rules for:
   - `22` (SSH)
   - `8000` (API) or use Nginx on `80/443`
3. SSH into instance and install Docker or Python runtime.

### Option A: Docker deploy
From project root:
```bash
docker build -f backend/Dockerfile -t pd-inference-api .
docker run -d --name pd-api -p 8000:8000 --env-file backend/.env pd-inference-api
```

### Option B: Native deploy
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 7) Environment Variables

All vars are prefixed with `PD_`:
- `PD_MODEL_SOURCE`: `local` or `s3`
- `PD_LOCAL_MODEL_DIR`: local folder path containing `.joblib` files
- `PD_S3_BUCKET`: required when using S3
- `PD_S3_PREFIX`: default `models`
- `PD_AWS_REGION`: default `us-east-1`

## 8) Model Path Strategy (Local vs S3)

- `local`: loads from `models/` by default (project root).
- `s3`: downloads all 3 model files once at startup to `/tmp/pd_models`, then serves inference from memory.

## 9) Scaling Later

- Run behind Nginx + systemd on EC2 for stability.
- Use multiple workers via Gunicorn/Uvicorn workers.
- Move to ECS/Fargate or EKS when traffic grows.
- Add Redis caching and request rate limiting.
- Add AWS ALB for load balancing and autoscaling.

## 10) Production Improvements (Optional)

- Add auth (API key/JWT)
- Add request tracing and structured JSON logs
- Add Prometheus metrics endpoint
- Add model versioning in response
- Add CI/CD pipeline (GitHub Actions + ECR + EC2/ECS deploy)
