from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routes.prediction_route import router as prediction_router 
from .services.prediction_services import prediction_service
from .routes.evidently_metrics_route import router as metrics_router
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan event moderne - DOIT ÊTRE AVANT app = FastAPI()
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Charger le modèle au démarrage de l'API
    """
    # Startup
    logger.info(" Démarrage de l'API...")
    
    if prediction_service.load_model():
        logger.info(" Modèle chargé avec succès")
    else:
        logger.warning(" API démarrée sans modèle")
    

    from .services.logging_service import prediction_logger
    prediction_logger.initialize_log_file()
    logger.info(" API prête!")
    
    yield  
    
    # Shutdown
    logger.info(" Arrêt de l'API...")

# Création de  l'app 
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
    lifespan=lifespan  # ← Passer le lifespan à l'app
)

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

app.include_router(metrics_router)

