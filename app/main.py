from fastapi import FastAPI
from routes.prediction_route import router as prediction_router 

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
)

app.include_router(prediction_router) 

@app.get("/")
async def root():
    return {
        "message": "API IoT Air Quality Monitoring",
        "status": "online",
        "version": "1.0.0"
    }