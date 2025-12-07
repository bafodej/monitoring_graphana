import pandas as pd
from fastapi import APIRouter, HTTPException
from loguru import logger
from datetime import datetime

from ..shemas.prediction_shemas import FeedbackInput
from ..config import AppConfig

router = APIRouter(prefix="/feedback", tags=["Feedback"])

def ensure_ground_truth_file_exists():
    """Crée le fichier de vérité terrain s'il n'existe pas."""
    try:
        AppConfig.GROUND_TRUTH_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not AppConfig.GROUND_TRUTH_LOG_PATH.exists():
            pd.DataFrame(columns=["prediction_id", "target", "timestamp"]).to_csv(
                AppConfig.GROUND_TRUTH_LOG_PATH, index=False
            )
            logger.info(f"Fichier de log de vérité terrain créé : {AppConfig.GROUND_TRUTH_LOG_PATH}")
    except Exception as e:
        logger.error(f"Impossible d'initialiser le fichier de vérité terrain : {e}")

# Vérification au démarrage
ensure_ground_truth_file_exists()

@router.post("/", status_code=201)
async def submit_feedback(feedback_data: FeedbackInput):
    """
    Permet de soumettre la vérité terrain pour une prédiction existante.
    """
    try:
        logger.info(f"Réception du feedback pour prediction_id={feedback_data.prediction_id}")

        # Préparer l'entrée à ajouter
        log_entry = {
            "prediction_id": feedback_data.prediction_id,
            "target": feedback_data.target,
            "timestamp": datetime.now().isoformat(),
        }

        # Écriture sécurisée dans le CSV
        pd.DataFrame([log_entry]).to_csv(
            AppConfig.GROUND_TRUTH_LOG_PATH, mode='a', header=False, index=False
        )

        logger.info(f"Feedback enregistré pour prediction_id={feedback_data.prediction_id}")
        return {"status": "success", "message": "Feedback enregistré avec succès."}

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'enregistrement du feedback : {e}"
        )
