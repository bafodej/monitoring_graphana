from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes.prediction_route import router as prediction_router 
from .services.prediction_services import prediction_service
import logging

# =========================
# Prometheus
# =========================
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# Métrique custom
# =========================
ventilation_metric = Gauge(
    "ventilation_required",
    "Indique si la ventilation doit être activée (1=Good, 0=Moderate/Poor)"
)

# =========================
# Lifespan event moderne
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Charger le modèle au démarrage de l'API
    """
    logger.info("Démarrage de l'API...")
    
    if prediction_service.load_model():
        logger.info("Modèle chargé avec succès")
    else:
        logger.warning("API démarrée sans modèle (mode dégradé)")
    
    # Instrumentator Prometheus
    Instrumentator().instrument(app).expose(app)
    logger.info("Prometheus metrics exposées sur /metrics")
    
    yield  
    
    logger.info("Arrêt de l'API...")

# =========================
# Création de l'app
# =========================
app = FastAPI(
    title="IoT Air Quality Monitoring API",
    description="""
    API REST pour monitorer la qualité de l'air intérieur et gérer le système de nettoyage.
    
    ## Fonctionnalités
    * Prédiction : Décider d'activer ou désactiver le nettoyage d'air
    * Monitoring : Métriques Prometheus pour Grafana
    * Logging : Enregistrement des prédictions pour Evidently AI
    """,
    version="1.0.0",
    lifespan=lifespan
)

# =========================
# Routes
# =========================
app.include_router(prediction_router) 

# =========================
# Routes de base
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
