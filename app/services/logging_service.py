import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

class PredictionLogger:
    """
    Service pour logger les prédictions dans un fichier CSV unique
    compatible avec Evidently et le monitoring.
    """

    def __init__(self):
        settings = get_settings()
        self.log_path: Path = settings.PREDICTION_LOG_PATH

        # colonnes cohérentes dans tout le pipeline
        self.columns = [
            "timestamp",
            "prediction_id",
            "temperature",
            "humidity",
            "co2",
            "pm25",
            "pm10",
            "tvoc",
            "occupancy",
            "prediction",
            "confidence",
            "action"
        ]

        self.initialize_log_file()

    def initialize_log_file(self):
        """Crée le CSV si vide."""
        try:
            if not self.log_path.exists():
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                df = pd.DataFrame(columns=self.columns)
                df.to_csv(self.log_path, index=False)
                logger.info(f"Fichier de log créé : {self.log_path}")
        except Exception as e:
            logger.error(f"Erreur initialisation log: {e}")

    def log_prediction(self, input_data: Dict[str, float], prediction_result: Dict[str, Any]):
        """
        Ajoute une ligne dans le fichier CSV Evidently.
        """
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "prediction_id": prediction_result.get("prediction_id"),
                "temperature": input_data["temperature"],
                "humidity": input_data["humidity"],
                "co2": input_data["co2"],
                "pm25": input_data["pm25"],
                "pm10": input_data["pm10"],
                "tvoc": input_data["tvoc"],
                "occupancy": input_data["occupancy"],
                "prediction": prediction_result["prediction"],
                "confidence": prediction_result["confidence"],
                "action": prediction_result["action"],
            }

            df = pd.DataFrame([entry])
            df.to_csv(self.log_path, mode="a", header=False, index=False)

            logger.debug(
                f"Log prédiction → {entry['prediction_id']} | {entry['action']}"
            )

        except Exception as e:
            logger.error(f"Erreur logging prédiction : {e}")

    # utilitaires
    def get_predictions_count(self) -> int:
        try:
            if not self.log_path.exists():
                return 0
            return len(pd.read_csv(self.log_path))
        except Exception:
            return 0

    def get_recent_predictions(self, n: int = 100) -> pd.DataFrame:
        try:
            if not self.log_path.exists():
                return pd.DataFrame()
            return pd.read_csv(self.log_path).tail(n)
        except Exception as e:
            logger.error(f"Erreur lecture prédictions: {e}")
            return pd.DataFrame()

    def get_all_predictions(self) -> pd.DataFrame:
        try:
            if not self.log_path.exists():
                return pd.DataFrame()
            return pd.read_csv(self.log_path)
        except Exception as e:
            logger.error(f"Erreur lecture prédictions: {e}")
            return pd.DataFrame()


prediction_logger = PredictionLogger()
