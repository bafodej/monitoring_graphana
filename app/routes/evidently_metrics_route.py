from fastapi import APIRouter
from pathlib import Path
import pandas as pd
import logging
from ..config import get_settings
from ..metrics import record_drift_metrics, ml_data_drift_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["Metrics"])

settings = get_settings()

@router.get("/evidently")
async def get_evidently_metrics():
    """
    Endpoint pour exposer les métriques Evidently au format JSON.
    Données statistiques des prédictions pour Grafana/Prometheus.
    """
    try:
        log_file: Path = settings.PREDICTION_LOG_PATH

        if not log_file.exists():
            return {
                "status": "no_data",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0,
                "features": {}
            }

        df = pd.read_csv(log_file)

        metrics = {
            "status": "ok",
            "predictions_count": len(df),
            "predictions_activate": int((df['prediction'] == 0).sum()) if not df.empty else 0,
            "predictions_deactivate": int((df['prediction'] == 1).sum()) if not df.empty else 0,
            "features": {}
        }

        feature_columns = ['temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy']
        for col in feature_columns:
            if col in df.columns:
                metrics["features"][col] = {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }

        return metrics

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques Evidently : {e}")
        return {"status": "error", "error": str(e)}


@router.get("/evidently/drift")
async def get_drift_status():
    """
    Statut du drift détecté par Evidently.
    Calcule le drift dynamique à partir des fichiers de référence et des logs.
    """
    try:
        reference_path: Path = settings.REFERENCE_DATA_PATH
        current_path: Path = settings.PREDICTION_LOG_PATH

        # Calcul dynamique du drift et mise à jour des métriques Prometheus
        record_drift_metrics(reference_path, current_path)

        drift_score = ml_data_drift_score._value.get()
        drift_detected = drift_score > 0.0

        return {
            "drift_detected": drift_detected,
            "drift_score": float(drift_score),
            "last_check": None  # possibilité d'ajouter un timestamp si nécessaire
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du drift : {e}")
        return {"status": "error", "error": str(e)}
