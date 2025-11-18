from fastapi import APIRouter, HTTPException
from shemas.prediction_shemas import AirQualityInput, PredictionOutput
# Import des vos schémas
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
    
    # TODO: Remplacer par une vraie prédiction quand le modèle sera prêt
    # Pour l'instant, simulation basée sur des seuils simples
    
    # Exemple de logique simple
    should_activate = data.co2 > 1000 or data.pm25 > 35 or data.co > 2.0
    
    prediction = 1 if should_activate else 0
    confidence = 0.85  # Valeur simulée
    
    return PredictionOutput(
        action="Activer" if prediction == 1 else "Désactiver",
        prediction=prediction,
        confidence=confidence,
        probability_activate=confidence if prediction == 1 else 1 - confidence,
        probability_deactivate=1 - confidence if prediction == 1 else confidence,
        timestamp=datetime.now().isoformat()
    )

