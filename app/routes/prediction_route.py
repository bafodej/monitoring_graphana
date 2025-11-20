from fastapi import APIRouter, HTTPException, Depends
from ..shemas.prediction_shemas import AirQualityInput, PredictionOutput
from ..services.prediction_services import prediction_service, AirQualityPredictionService
from ..services.logging_service import prediction_logger
from ..metrics import ventilation_metric
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
    Endpoint pour prédire si la ventilation doit être activée.
    Renvoie :
        1 = Good (pas besoin de ventilation)
        0 = Moderate/Poor (ventilation nécessaire)
    """
    if not service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded, API is in degraded mode."
        )

    try:
        features = data.model_dump()
        
        # Prédiction binaire
        binary_pred = service.predict(features)

        # Met à jour Prometheus
        ventilation_metric.set(binary_pred)

        # Logger la prédiction pour Evidently
        action = "Désactiver" if binary_pred == 1 else "Activer"
        prediction_logger.log_prediction(
            input_data=features,
            prediction_result={'prediction': binary_pred, 'action': action}
        )

        logger.info(f"Prédiction: {binary_pred}, action: {action}")

        # Retourne la réponse API
        return PredictionOutput(prediction=binary_pred)

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during prediction: {str(e)}"
        )
