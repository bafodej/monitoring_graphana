from pathlib import Path
import pandas as pd
from loguru import logger
from evidently.legacy.report import Report
from evidently.legacy.metrics import DataDriftTable
from ..metrics import record_drift_metrics, ml_data_drift_score
from ..config import get_settings

settings = get_settings()

class EvidentlyService:
    """
    Service pour exposer les métriques Evidently pour Grafana/Prometheus.
    """

    def __init__(self):
        self.reference_path: Path = settings.REFERENCE_DATA_PATH
        self.prediction_log_path: Path = settings.PREDICTION_LOG_PATH
        self.feature_columns: list[str] = settings.FEATURE_COLUMNS

    def get_prediction_metrics(self) -> dict:
        """
        Retourne des statistiques sur les prédictions pour Grafana/Prometheus.
        """
        if not self.prediction_log_path.exists() or self.prediction_log_path.stat().st_size == 0:
            return {
                "status": "no_data",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0,
                "features": {}
            }

        try:
            df = pd.read_csv(self.prediction_log_path)
        except Exception as e:
            logger.error(f"Impossible de lire le fichier de prédictions : {e}")
            return {
                "status": "error",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0,
                "features": {}
            }

        # Vérification colonne 'predicted_class'
        pred_col = "predicted_class"
        if pred_col not in df.columns:
            logger.warning(f"Colonne '{pred_col}' manquante dans le CSV, remplissage par 'unknown'")
            df[pred_col] = "unknown"

        metrics = {
            "status": "ok",
            "predictions_count": len(df),
            "predictions_activate": int((df[pred_col] == "activate_ventilation").sum()),
            "predictions_deactivate": int((df[pred_col] == "deactivate_ventilation").sum()),
            "features": {}
        }

        # Statistiques sur les features
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
        """
        Calcule le drift des données, met à jour Prometheus, retourne score et status.
        """
        if not self.reference_path.exists():
            logger.warning(f"Fichier de référence manquant : {self.reference_path}")
            return {"status": "no_data", "drift_detected": False, "drift_score": 0.0}

        if not self.prediction_log_path.exists() or self.prediction_log_path.stat().st_size == 0:
            logger.warning(f"Fichier de log des prédictions vide ou manquant : {self.prediction_log_path}")
            return {"status": "no_data", "drift_detected": False, "drift_score": 0.0}

        try:
            record_drift_metrics(self.reference_path, self.prediction_log_path)
            # Récupération sécurisée de la valeur Prometheus
            drift_score = getattr(ml_data_drift_score._value, "get", lambda: 0)()
            drift_score = float(drift_score) if drift_score is not None else 0.0
            drift_detected = drift_score > 0.0
            status = "ok"
        except Exception as e:
            logger.error(f"Erreur lors du calcul du drift : {e}")
            drift_score = 0.0
            drift_detected = False
            status = "error"

        return {
            "status": status,
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "last_check": pd.Timestamp.now().isoformat()
        }
