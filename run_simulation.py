import requests
import time
import logging
import os
from app.config import AppConfig

# Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

# URL de l'API
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
FEEDBACK_ENDPOINT = f"{API_BASE_URL}/feedback"

# Échantillons de test
SAMPLE_TESTS = [
    {"temperature": 28.0, "humidity": 70.0, "co2": 1800, "pm25": 80.0, "pm10": 120.0, "tvoc": 400, "occupancy": 50},
    {"temperature": 30.0, "humidity": 50.0, "co2": 500, "pm25": 10.0, "pm10": 15.0, "tvoc": 50, "occupancy": 5},
    {"temperature": 22.0, "humidity": 45.0, "co2": 400, "pm25": 8.0, "pm10": 12.0, "tvoc": 30, "occupancy": 0},
    {"temperature": 24.0, "humidity": 55.0, "co2": 1200, "pm25": 40.0, "pm10": 60.0, "tvoc": 250, "occupancy": 30}
]

GROUND_TRUTH = [0, 0, 1, 0]  # 0 = activer ventilation, 1 = désactiver

def run_simulation():
    logging.info("--- DÉBUT DE LA SIMULATION ---")
    prediction_ids = []

    # --- Étape 1 : Prédictions ---
    for i, data in enumerate(SAMPLE_TESTS):
        try:
            logging.info(f"Envoi de la prédiction #{i+1}")
            response = requests.post(PREDICT_ENDPOINT, json=data)
            response.raise_for_status()
            pid = response.json().get("prediction_id")
            prediction_ids.append(pid)
            logging.info(f"Prédiction #{i+1} réussie, ID={pid}")
        except requests.RequestException as e:
            logging.error(f"Erreur prédiction #{i+1} : {e}")
        time.sleep(1)

    if not prediction_ids:
        logging.error("Aucune prédiction réussie. Simulation arrêtée.")
        return

    # --- Étape 2 : Feedback ---
    for i, pid in enumerate(prediction_ids):
        feedback_data = {"prediction_id": pid, "target": GROUND_TRUTH[i]}
        try:
            logging.info(f"Envoi du feedback #{i+1} pour prediction_id={pid}")
            response = requests.post(FEEDBACK_ENDPOINT, json=feedback_data)
            response.raise_for_status()
            logging.info(f"Feedback #{i+1} enregistré avec succès")
        except requests.RequestException as e:
            logging.error(f"Erreur feedback #{i+1} : {e}")
        time.sleep(1)

    # --- Étape 3 : Test URL inexistante ---
    try:
        response = requests.get(f"{API_BASE_URL}/ceci-est-une-fausse-url")
        if response.status_code == 404:
            logging.info("Test URL inexistante OK (404 attendu)")
        else:
            logging.warning(f"Test URL inexistante retour inattendu : {response.status_code}")
    except Exception as e:
        logging.warning(f"Erreur attendue 404 : {e}")

    logging.info("--- SIMULATION TERMINÉE ---")

if __name__ == "__main__":
    run_simulation()
