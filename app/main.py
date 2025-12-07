from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
import logging

from .routes.prediction_route import router as prediction_router
from .routes.feedback_route import router as feedback_router
from .services.prediction_services import prediction_service

# 🔥 Import des métriques depuis metrics.py (source unique)
from .metrics import (
    ml_model_accuracy,
    ml_data_drift_score,
    ml_predictions_total,
    ml_prediction_confidence,
    ml_prediction_latency_seconds
)

import time

# =========================
# Logging global
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =========================
# FastAPI Lifespan
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage de l'API...")

    # Charger le modèle
    if prediction_service.load_model():
        logger.info("Modèle chargé avec succès")
        # Valeur initiale
        ml_model_accuracy.labels(model_version="v1").set(0.0)
    else:
        logger.warning("API démarrée sans modèle")

    yield

    logger.info("Arrêt de l'API...")


# =========================
# FastAPI App
# =========================
app = FastAPI(
    title="IoT Air Quality Monitoring API",
    description="API REST pour monitorer la qualité de l'air intérieur et gérer le système de ventilation.",
    version="1.0.0",
    lifespan=lifespan
)


# =========================
# Prometheus Instrumentator
# =========================
instrumentator = Instrumentator(should_group_status_codes=False)
instrumentator.instrument(app).expose(app)
logger.info("Metrics Prometheus exposées sur /metrics")


# =========================
# Routes
# =========================
app.include_router(prediction_router)
app.include_router(feedback_router)


# =========================
# Endpoints génériques
# =========================
@app.get("/")
async def root():
    return {
        "message": "API IoT Air Quality Monitoring",
        "status": "online",
        "version": "1.0.0",
        "model_loaded": prediction_service.is_loaded()
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy" if prediction_service.is_loaded() else "degraded",
        "model_loaded": prediction_service.is_loaded()
    }


# =========================
# Fonction utilitaire pour enregistrer les métriques ML
# =========================
def record_prediction(model_version: str, prediction_class: str, confidence: float, latency: float, accuracy: float = None, drift_score: float = None):
    ml_predictions_total.labels(model_version=model_version, prediction_class=prediction_class).inc()
    ml_prediction_latency_seconds.labels(model_version=model_version).observe(latency)
    ml_prediction_confidence.labels(model_version=model_version, prediction_class=prediction_class).set(confidence)

    if accuracy is not None:
        ml_model_accuracy.labels(model_version=model_version).set(accuracy)

    if drift_score is not None:
        ml_data_drift_score.set(drift_score)

    logger.info(f"Prediction enregistrée: {model_version=} {prediction_class=} {confidence=} {latency=}")
