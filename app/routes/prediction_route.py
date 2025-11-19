from fastapi import APIRouter, HTTPException, Depends
from ..shemas.prediction_shemas import AirQualityInput, PredictionOutput
from ..services.prediction_services import prediction_service, AirQualityPredictionService
from ..services.logging_service import prediction_logger  # ← Import du logger
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Prediction"]
)

@router.post("/predict", response_model=PredictionOutput)
async def predict(
    data: AirQualityInput,
    service: AirQualityPredictionService = Depends(lambda: prediction_service)
):
    """
    Endpoint to predict if ventilation is required.
    Renvoie uniquement 1 (Good = pas besoin) ou 0 (Moderate/Poor = ventilation nécessaire)
    """
    if not service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded, API is in degraded mode."
        )

    try:
        features = data.model_dump()
        
        # Prédiction binaire seulement
        binary_pred = service.predict(features)
        
        # Créer la réponse
        response = PredictionOutput(prediction=binary_pred)
        
        # Logger la prédiction (calculer action en interne pour le log)
        action = "Désactiver" if binary_pred == 1 else "Activer"
        prediction_logger.log_prediction(
            input_data=features,
            prediction_result={
                'prediction': response.prediction,
                'action': action  # Juste pour le CSV
            }
        )
        
        logger.info(f" Prédiction: {binary_pred}")
        
        return response

    except Exception as e:
        logger.error(f" Erreur: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during prediction: {str(e)}"
        )

