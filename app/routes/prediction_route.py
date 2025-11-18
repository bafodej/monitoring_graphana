from fastapi import APIRouter, HTTPException
from ..shemas.prediction_shemas import AirQualityInput, PredictionOutput
# Import des  schémas
# Import du service de prédiction (quand il existera)

router = APIRouter(
    prefix="/api",  # Tous les endpoints commenceront par /api
    tags=["Prediction"]
)

@router.post("/predict", response_model=PredictionOutput)
async def predict(data: AirQualityInput):
    """
    Endpoint de prédiction (mode mock en attendant le modèle)
    """
    from datetime import datetime
    
    # TODO: A Remplacer par une vraie prédiction quand le modèle sera prêt
    # Pour l'instant, simulation basée sur des seuils
    
    # Score de risque basé sur plusieurs facteurs
    risk_score = 0
    
    # Vérifier CO2 (seuil: 1000 ppm)
    if data.co2 > 1000:
        risk_score += 3
    elif data.co2 > 800:
        risk_score += 1
    
    # Vérifier PM2.5 (seuil: 35 µg/m³)
    if data.pm25 > 35:
        risk_score += 3
    elif data.pm25 > 25:
        risk_score += 1
    
    # Vérifier PM10 (seuil: 50 µg/m³)
    if data.pm10 > 50:
        risk_score += 2
    
    # Vérifier TVOC (seuil: 500 ppb)
    if data.tvoc > 500:
        risk_score += 2
    elif data.tvoc > 300:
        risk_score += 1
    
    # Vérifier humidité (seuil: 60%)
    if data.humidity > 70 or data.humidity < 30:
        risk_score += 1
    
    # Vérifier température (seuil confort: 18-25°C)
    if data.temperature > 28 or data.temperature < 18:
        risk_score += 1
    
    # Facteur occupancy (plus de personnes = plus de pollution)
    if data.occupancy > 5:
        risk_score += 1
    
    # Décision basée sur le score de risque
    should_activate = risk_score >= 4
    
    prediction = 0 if should_activate else 1
    
    # Calculer la confiance basée sur le score
    confidence = min(0.95, 0.65 + (risk_score * 0.05))
    
    return PredictionOutput(
        prediction=prediction,
    )

