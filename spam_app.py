# Spam detection API v2, /healthz now reports the version
import os
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_VERSION = "v2"
MODEL_PATH = os.environ.get("MODEL_PATH", "data/model.joblib")

app = FastAPI(title="Spam Detection API")
_model = None


@app.on_event("startup")
def load_model():
    global _model
    _model = joblib.load(MODEL_PATH)
    print(f"loaded model from {MODEL_PATH}, version {APP_VERSION}")


class PredictRequest(BaseModel):
    text: str

@app.get("/healthz")
def healthz():
    if _model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ok", "version": APP_VERSION}


@app.post("/predict")
def predict(request: PredictRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"label": _model.predict([request.text]).tolist()[0]}
