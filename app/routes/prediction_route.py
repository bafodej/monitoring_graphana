import time
import uuid
from fastapi import APIRouter, HTTPException
from loguru import logger

from ..shemas.prediction_shemas import AirQualityInput, PredictionOutput
from ..services.prediction_services import prediction_service
from ..services.logging_service import prediction_logger
from ..metrics import (
    record_prediction_metrics,
    record_sensor_data,
    record_api_error,
    ventilation_status,
    ventilation_activations_total
)

router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]
)

@router.post("/", response_model=PredictionOutput)
async def make_prediction(
    input_data: AirQualityInput
):
    """
    Accepte les données des capteurs de qualité de l'air, effectue une prédiction
    et retourne la nécessité d'activer la ventilation.

    Chaque prédiction est enregistrée avec un ID unique.
    """
    if not prediction_service.is_loaded():
        record_api_error("model_not_loaded")
        raise HTTPException(
            status_code=503,
            detail="Le modèle de prédiction n'est pas chargé. API en mode dégradé."
        )

    try:
        prediction_id = str(uuid.uuid4())
        features = input_data.dict()
        start_time = time.time()

        # Effectuer la prédiction pour obtenir la classe et la probabilité
        binary_pred, probability = prediction_service.predict_with_proba(features)

        latency = time.time() - start_time

        # Déterminer la classe de prédiction textuelle
        prediction_class = "activate_ventilation" if binary_pred == 0 else "deactivate_ventilation"

        # Enregistrer les métriques de la prédiction ML
        record_prediction_metrics(
            model_version=prediction_service.get_model_version(),
            prediction_class=prediction_class,
            confidence=float(probability),
            latency=latency
        )

        # Enregistrer les données des capteurs en tant que métriques
        record_sensor_data(features)

        # Mettre à jour les métriques métier
        ventilation_status.set(binary_pred)
        if binary_pred == 0:  # 0 signifie que la ventilation est nécessaire
            ventilation_activations_total.inc()

        # Logger la prédiction pour le rapport Evidently
        action = "Activer" if binary_pred == 0 else "Désactiver"
        prediction_logger.log_prediction(
            prediction_id=prediction_id,
            input_data=features,
            prediction_result={'prediction': binary_pred, 'action': action, 'probability': float(probability)}
        )

        logger.info(f"Prédiction {prediction_id}: {action} (Confiance: {probability:.2f}, Latence: {latency:.4f}s)")

        # Retourner la réponse API
        return PredictionOutput(
            prediction_id=prediction_id,
            prediction=binary_pred,
            confidence=float(probability)
        )

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        record_api_error("prediction_error")
        raise HTTPException(
            status_code=500,
            detail=f"Une erreur est survenue pendant la prédiction: {str(e)}"
        )