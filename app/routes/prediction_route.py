from fastapi import APIRouter, HTTPException, Depends
from ..shemas.prediction_shemas import AirQualityInput, PredictionOutput
from ..services.prediction_services import prediction_service, AirQualityPredictionService
from prometheus_client import Gauge

# Création d'une métrique Prometheus custom
ventilation_metric = Gauge(
    "ventilation_required",
    "Indique si la ventilation doit être activée (1=Good, 0=Moderate/Poor)"
)

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
        
        # Prédiction binaire + label + confiance
        binary_pred, label, confidence = service.predict(features)
        
        # Met à jour la métrique Prometheus
        ventilation_metric.set(binary_pred)
        
        return PredictionOutput(prediction=binary_pred)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during prediction: {str(e)}"
        )
