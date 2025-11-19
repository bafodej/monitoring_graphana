from fastapi import APIRouter, HTTPException, Depends
from ..shemas.prediction_shemas import AirQualityInput, PredictionOutput
from ..services.prediction_services import prediction_service, AirQualityPredictionService
from ..metrics import ventilation_metric

router = APIRouter(
    prefix="/api",
    tags=["Prediction"]
)

@router.post("/predict", response_model=PredictionOutput)
async def predict(
    data: AirQualityInput,
    service: AirQualityPredictionService = Depends(lambda: prediction_service)
):

    if not service.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded, API is in degraded mode."
        )

    try:
        features = data.model_dump()

        # On récupère seulement la prédiction binaire
        binary_pred = service.predict(features)

        # Met à jour Prometheus
        ventilation_metric.set(binary_pred)

        # Retourne à l'API
        return PredictionOutput(prediction=binary_pred)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during prediction: {str(e)}"
        )
