import pandas as pd
from pathlib import Path
from datetime import datetime
from loguru import logger
from ..config import get_settings

settings = get_settings()

class FeedbackService:
    def __init__(self):
        self.ground_truth_path: Path = settings.GROUND_TRUTH_LOG_PATH
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        try:
            self.ground_truth_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.ground_truth_path.exists():
                pd.DataFrame(columns=["prediction_id", "target", "timestamp"]).to_csv(
                    self.ground_truth_path, index=False
                )
                logger.info(f"Fichier de log de vérité terrain créé : {self.ground_truth_path}")
        except Exception as e:
            logger.error(f"Impossible d'initialiser le fichier de vérité terrain : {e}")

    def submit_feedback(self, prediction_id: str, target: int) -> None:
        """Enregistre un feedback dans le CSV."""
        try:
            log_entry = {
                "prediction_id": prediction_id,
                "target": target,
                "timestamp": datetime.now().isoformat(),
            }
            pd.DataFrame([log_entry]).to_csv(
                self.ground_truth_path, mode='a', header=False, index=False
            )
            logger.info(f"Feedback enregistré pour prediction_id={prediction_id}")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback : {e}")
            raise
