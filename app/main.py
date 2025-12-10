from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger

from .routes.prediction_route import router as prediction_router
from .routes.feedback_route import router as feedback_router
from .routes.evidently_metrics_route import router as evidently_metrics_router
from .services.prediction_services import prediction_service
from .services.logging_service import prediction_logger
from .metrics import (
    ml_model_accuracy,
    ml_data_drift_score,
    ml_predictions_total,
    ml_prediction_confidence,
    ml_prediction_latency_seconds
)
from .config import get_settings

settings = get_settings()

# ----------------------------------------------------------------------
# LIFESPAN
# ----------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage de l'API...")

    # Charger le modèle
    if prediction_service.load_model():
        logger.info("Modèle chargé avec succès")
    else:
        logger.warning("API démarrée sans modèle")

    # Initialiser le CSV de log pour Evidently
    prediction_logger.initialize_log_file()

    yield
    logger.info("Arrêt de l'API...")


# ----------------------------------------------------------------------
# APPLICATION
# ----------------------------------------------------------------------
app = FastAPI(
    title="IoT Air Quality Monitoring API",
    description="API REST pour monitorer la qualité de l'air intérieur.",
    version="1.0.0",
    lifespan=lifespan
)

# Prometheus
instrumentator = Instrumentator(should_group_status_codes=False)
instrumentator.instrument(app).expose(app)
logger.info("Metrics Prometheus exposées sur /metrics")

# Routers
app.include_router(prediction_router)
app.include_router(feedback_router)
app.include_router(evidently_metrics_router)


# ----------------------------------------------------------------------
# ENDPOINTS GÉNÉRAUX
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# FONCTION UTILITAIRE POUR ENREGISTRER LES PREDICTIONS
# ----------------------------------------------------------------------
def record_prediction(features: dict, prediction_class: str, confidence: float, latency: float,
                      accuracy: float = None, drift_score: float = None):
    """
    Enregistre à la fois :
    - les métriques Prometheus
    - le CSV pour Evidently
    """
    model_version = prediction_service.get_model_version()

    # 1) Prometheus
    ml_predictions_total.labels(model_version=model_version, prediction_class=prediction_class).inc()
    ml_prediction_latency_seconds.labels(model_version=model_version).observe(latency)
    ml_prediction_confidence.labels(model_version=model_version, prediction_class=prediction_class).set(confidence)

    if accuracy is not None:
        ml_model_accuracy.labels(model_version=model_version).set(accuracy)
    if drift_score is not None:
        ml_data_drift_score.set(drift_score)

    # 2) CSV Evidently
    action = "Activer" if prediction_class == "activate_ventilation" else "Désactiver"
    prediction_logger.log_prediction(features, {"prediction": 0 if prediction_class == "activate_ventilation" else 1,
                                                "action": action})

    logger.info(f"Prediction enregistrée | version={model_version}, "
                f"class={prediction_class}, confidence={confidence:.3f}, latency={latency:.4f}s")
