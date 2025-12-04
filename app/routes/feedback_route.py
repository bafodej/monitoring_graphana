import pandas as pd
from fastapi import APIRouter, HTTPException
from loguru import logger
import datetime

from ..shemas.prediction_shemas import FeedbackInput
from ..config import AppConfig  # Importer la configuration centralisée

# Crée le routeur pour le feedback
router = APIRouter(prefix="/feedback", tags=["Feedback"])

def initialize_ground_truth_log():
    """Crée le fichier de log pour la vérité terrain s'il n'existe pas."""
    try:
        AppConfig.GROUND_TRUTH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not AppConfig.GROUND_TRUTH_LOG_PATH.exists():
            df = pd.DataFrame(columns=["prediction_id", "target", "timestamp"])
            df.to_csv(AppConfig.GROUND_TRUTH_LOG_PATH, index=False)
            logger.info(f"Fichier de log de vérité terrain créé: {AppConfig.GROUND_TRUTH_LOG_PATH}")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du log de vérité terrain: {e}")

# Initialise le fichier de log au démarrage de l'application
initialize_ground_truth_log()

@router.post("/", status_code=201)
async def submit_feedback(feedback_data: FeedbackInput):
    """
    Permet de soumettre la vérité terrain (ground truth) pour une prédiction existante.
    """
    try:
        logger.info(f"Réception du feedback pour l'ID de prédiction: {feedback_data.prediction_id}")

        # Prépare l'entrée de log
        log_entry = {
            "prediction_id": feedback_data.prediction_id,
            "target": feedback_data.target,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Ajoute l'entrée au fichier CSV
        df = pd.DataFrame([log_entry])
        df.to_csv(AppConfig.GROUND_TRUTH_LOG_PATH, mode='a', header=False, index=False)

        return {"status": "success", "message": "Feedback enregistré avec succès."}

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Une erreur interne est survenue lors de l'enregistrement du feedback: {e}"
        )
