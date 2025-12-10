from pathlib import Path
import pandas as pd
from loguru import logger
from evidently.legacy.report import Report
from evidently.legacy.metrics import DataDriftTable
from ..metrics import record_drift_metrics, ml_data_drift_score
from ..config import get_settings

settings = get_settings()

class EvidentlyService:
    def __init__(self):
        self.reference_path = settings.REFERENCE_DATA_PATH
        self.prediction_log_path = settings.PREDICTION_LOG_PATH
        self.feature_columns = settings.FEATURE_COLUMNS

    def get_prediction_metrics(self) -> dict:
        """Retourne statistiques des prédictions pour Grafana/Prometheus"""
        if not self.prediction_log_path.exists() or self.prediction_log_path.stat().st_size == 0:
            return {
                "status": "no_data",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0,
                "features": {}
            }

        df = pd.read_csv(self.prediction_log_path)

        # Colonne de prédiction correcte
        pred_col = "predicted_class"

        # Compter les classes en ignorant 'unknown'
        metrics = {
            "status": "ok",
            "predictions_count": len(df),
            "predictions_activate": int((df[pred_col] == "activate_ventilation").sum()),
            "predictions_deactivate": int((df[pred_col] == "deactivate_ventilation").sum()),
            "features": {}
        }

        # Statistiques des features
        for col in self.feature_columns:
            if col in df.columns:
                metrics["features"][col] = {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }

        return metrics

    def compute_drift(self) -> dict:
        """Calcule le drift, met à jour Prometheus, retourne score et status"""
        if not self.reference_path.exists() or not self.prediction_log_path.exists():
            return {"status": "no_data", "drift_detected": False, "drift_score": 0.0}

        try:
            record_drift_metrics(self.reference_path, self.prediction_log_path)
            drift_score = float(ml_data_drift_score._value.get())
            drift_detected = drift_score > 0.0
        except Exception as e:
            logger.error(f"Erreur lors du calcul du drift : {e}")
            drift_score = 0.0
            drift_detected = False

        return {
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "last_check": pd.Timestamp.now().isoformat()
        }
