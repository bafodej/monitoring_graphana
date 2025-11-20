from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes.prediction_route import router as prediction_router
from .routes.evidently_metrics_route import router as metrics_router
from .services.prediction_services import prediction_service
from .metrics import ventilation_metric
from prometheus_fastapi_instrumentator import Instrumentator
import logging

# =========================
# Logging global
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# Lifespan (startup / shutdown)
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
        from .services.logging_service import prediction_logger
        prediction_logger.initialize_log_file()
        logger.info("Fichier de logs Evidently initialisé")
    except Exception as e:
        logger.error(f"Impossible d'initialiser logging Evidently : {e}")

    logger.info("API prête !")
    yield

    # -------------------------------------
    logger.info("Arrêt de l'API...")

# =========================
# Application FastAPI
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
# Prometheus instrumentation
# =========================
instrumentator = Instrumentator(
    should_group_status_codes=False
)
instrumentator.instrument(app).expose(app)
logger.info("Metrics Prometheus exposées sur /metrics")

# =========================
# Routes
# =========================
app.include_router(prediction_router)
app.include_router(metrics_router)

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
