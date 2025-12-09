import time
from typing import List, Dict
import requests
from loguru import logger
from app.config import get_settings

# --- Configuration ---
settings = get_settings()
API_BASE_URL: str = settings.API_BASE_URL if hasattr(settings, "API_BASE_URL") else "http://api:8000"
PREDICT_ENDPOINT: str = f"{API_BASE_URL}/predict"
FEEDBACK_ENDPOINT: str = f"{API_BASE_URL}/feedback"

# --- Échantillons de test ---
SAMPLE_TESTS: List[Dict] = [
    {"temperature": 28.0, "humidity": 70.0, "co2": 1800, "pm25": 80.0, "pm10": 120.0, "tvoc": 400, "occupancy": 50},
    {"temperature": 30.0, "humidity": 50.0, "co2": 500, "pm25": 10.0, "pm10": 15.0, "tvoc": 50, "occupancy": 5},
    {"temperature": 22.0, "humidity": 45.0, "co2": 400, "pm25": 8.0, "pm10": 12.0, "tvoc": 30, "occupancy": 0},
    {"temperature": 24.0, "humidity": 55.0, "co2": 1200, "pm25": 40.0, "pm10": 60.0, "tvoc": 250, "occupancy": 30},
]

GROUND_TRUTH: List[int] = [0, 0, 1, 0]  # 0 = activer ventilation, 1 = désactiver


def run_simulation() -> None:
    """Exécute la simulation complète : prédictions + feedback + test URL 404."""
    logger.info("=== DÉBUT DE LA SIMULATION ===")
    prediction_ids: List[str] = []

    # --- Étape 1 : Prédictions ---
    for i, sample in enumerate(SAMPLE_TESTS, start=1):
        try:
            logger.info(f"Envoi prédiction #{i}")
            response = requests.post(PREDICT_ENDPOINT, json=sample, timeout=5)
            response.raise_for_status()
            pid = response.json().get("prediction_id")
            if pid:
                prediction_ids.append(pid)
                logger.success(f"Prédiction #{i} réussie | ID={pid}")
            else:
                logger.warning(f"Prédiction #{i} OK mais pas d'ID retourné")
        except requests.RequestException as e:
            logger.error(f"Erreur prédiction #{i} : {e}")
        time.sleep(1)

    if not prediction_ids:
        logger.error("Aucune prédiction réussie. Simulation arrêtée.")
        return

    # --- Étape 2 : Feedback ---
    for i, pid in enumerate(prediction_ids):
        feedback_payload = {"prediction_id": pid, "target": GROUND_TRUTH[i]}
        try:
            logger.info(f"Envoi feedback #{i+1} pour prediction_id={pid}")
            response = requests.post(FEEDBACK_ENDPOINT, json=feedback_payload, timeout=5)
            response.raise_for_status()
            logger.success(f"Feedback #{i+1} enregistré")
        except requests.RequestException as e:
            logger.error(f"Erreur feedback #{i+1} : {e}")
        time.sleep(1)

    # --- Étape 3 : Test URL inexistante ---
    try:
        response = requests.get(f"{API_BASE_URL}/ceci-est-une-fausse-url", timeout=5)
        if response.status_code == 404:
            logger.info("Test URL inexistante OK (404 attendu)")
        else:
            logger.warning(f"Test URL inexistante retour inattendu : {response.status_code}")
    except requests.RequestException as e:
        logger.warning(f"Erreur attendue lors du test URL inexistante : {e}")

    logger.info("=== SIMULATION TERMINÉE ===")


if __name__ == "__main__":
    run_simulation()
