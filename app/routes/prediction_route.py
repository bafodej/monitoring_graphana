import uuid
import time
from fastapi import APIRouter, HTTPException
from loguru import logger

from ..schemas.prediction_schemas import AirQualityInput, PredictionOutput
from ..services.prediction_services import prediction_service
from ..metrics import (
    record_prediction_metrics,
    record_sensor_data,
    record_api_error,
    ventilation_status,
    ventilation_activations_total,
)

router = APIRouter(
    prefix="/predict",
    tags=["Predictions"],
)


@router.post("/", response_model=PredictionOutput)
async def make_prediction(input_data: AirQualityInput):
    """
    Reçoit les données des capteurs, exécute une prédiction et retourne
    si la ventilation doit être activée ou non, ainsi que la confiance associée.

    Chaque prédiction est tracée via un ID unique.
    """

    if not prediction_service.is_loaded():
        record_api_error("model_not_loaded")
        raise HTTPException(
            status_code=503,
            detail="Le modèle de prédiction n'est pas chargé. API en mode dégradé.",
        )

    try:
        prediction_id = str(uuid.uuid4())
        features = input_data.model_dump()

        start_time = time.perf_counter()

        # --- Prédiction ---
        binary_pred, probability = prediction_service.predict_with_proba(features)

        latency = time.perf_counter() - start_time

        # 0 = poor/moderate → activer ventilation
        prediction_class = (
            "activate_ventilation" if binary_pred == 0 else "deactivate_ventilation"
        )

        # --- Metrics ML ---
        record_prediction_metrics(
            model_version=prediction_service.get_model_version(),
            prediction_class=prediction_class,
            confidence=float(probability),
            latency=latency,
        )

        # --- Metrics capteurs ---
        record_sensor_data(features)

        # --- Business logic metrics ---
        ventilation_status.set(binary_pred)
        if binary_pred == 0:
            ventilation_activations_total.inc()

        # --- Logging propre ---
        action = "Activer" if binary_pred == 0 else "Désactiver"
        logger.info(
            f"[Prediction {prediction_id}] {action} ventilation | "
            f"Confiance={probability:.2f} | Latence={latency:.4f}s"
        )

        return PredictionOutput(
            prediction_id=prediction_id,
            prediction=binary_pred,
            confidence=float(probability),
        )

    except Exception as e:
        logger.exception("Erreur pendant la prédiction")
        record_api_error("prediction_error")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne pendant la prédiction: {str(e)}",
        )
