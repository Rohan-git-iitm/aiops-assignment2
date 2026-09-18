# Spam detection API with an optional Redis cache
import os
import time
import joblib
import redis
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

MODEL_PATH = os.environ.get("MODEL_PATH", "data/model.joblib")
REDIS_HOST = os.environ.get("REDIS_HOST")  # if not set, then API runs without cache
CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))

app = FastAPI(title="Spam Detection API")
_model = None
cache = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True) if REDIS_HOST else None


@app.on_event("startup")
def load_model():
    global _model
    _model = joblib.load(MODEL_PATH)
    print(f"loaded model from {MODEL_PATH}, cache host: {REDIS_HOST}", flush=True)


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    if _model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest, response: Response):
    if _model is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    t0 = time.perf_counter()
    key = f"pred:{request.text}"
    label = cache.get(key) if cache else None

    if label is not None:
        status = "HIT"
    else:
        label = _model.predict([request.text]).tolist()[0]
        if cache:
            cache.set(key, label, ex=CACHE_TTL)
        status = "MISS"

    elapsed_ms = (time.perf_counter() - t0) * 1000
    response.headers["X-Cache"] = status
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.3f}"
    print(f"cache {status} ({elapsed_ms:.3f} ms): {request.text[:40]!r}", flush=True)
    return {"label": label}
