from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
import logging
import time

from .routes.prediction_route import router as prediction_router
from .routes.evidently_metrics_route import router as metrics_router
from .routes.feedback_route import router as feedback_router
from .services.prediction_services import prediction_service
from .services.logging_service import prediction_logger
from .metrics import (
    ml_predictions_total, ml_prediction_latency_seconds,
    ml_model_accuracy, ml_data_drift_score,
    ml_prediction_confidence
)

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

    # Charger le modèle ML
    if prediction_service.load_model():
        logger.info("Modèle chargé avec succès")
    else:
        logger.warning("API démarrée sans modèle (mode dégradé)")

    # Initialiser le fichier de logs Evidently
    try:
        prediction_logger.initialize_log_file()
        logger.info("Fichier de logs Evidently initialisé")
    except Exception as e:
        logger.error(f"Impossible d'initialiser logging Evidently : {e}")

    logger.info("API prête !")
    yield
    logger.info("Arrêt de l'API...")

# =========================
# FastAPI App
# =========================
app = FastAPI(
    title="IoT Air Quality Monitoring API",
    description="""
    API REST pour monitorer la qualité de l'air intérieur et gérer le système de ventilation.

    ## Fonctionnalités
    - 🔮 Prédiction ML : déterminer si la ventilation doit être activée
    - 📈 Monitoring Prometheus / Grafana
    - 📊 Evidently : suivi de dérive et qualité de modèle
    """,
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
app.include_router(metrics_router)
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
