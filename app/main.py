from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes.prediction_route import router as prediction_router
from .services.prediction_services import prediction_service
from .metrics import ventilation_metric
from prometheus_fastapi_instrumentator import Instrumentator
import logging

# =========================
# Logging
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =========================
# Lifespan (chargement modèle)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Démarrage de l'API...")

    if prediction_service.load_model():
        logger.info("Modèle chargé avec succès")
    else:
        logger.warning("API démarrée sans modèle (mode dégradé)")

    yield

    logger.info("Arrêt de l'API...")


# =========================
# Création de l'app
# =========================
app = FastAPI(
    title="IoT Air Quality Monitoring API",
    version="1.0.0",
    lifespan=lifespan
)

# Instrumentator doit être ajouté **ici**
Instrumentator().instrument(app).expose(app)
logger.info("Prometheus metrics exposées sur /metrics")

# Routes
app.include_router(prediction_router)


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
