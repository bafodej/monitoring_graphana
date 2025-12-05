import requests
import time
import logging
from typing import List, Dict, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

# --- CONFIGURATION DE LA SIMULATION ---
API_BASE_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
FEEDBACK_ENDPOINT = f"{API_BASE_URL}/feedback"
UPDATE_REPORTS_ENDPOINT = f"{API_BASE_URL}/metrics/evidently/update-reports"

# Données de test fournies
SAMPLE_TESTS: List[Dict[str, Any]] = [
    {"temperature": 28.0, "humidity": 70.0, "co2": 1800, "pm25": 80.0, "pm10": 120.0, "tvoc": 400, "occupancy": 50},
    {"temperature": 30.0, "humidity": 50.0, "co2": 500, "pm25": 10.0, "pm10": 15.0, "tvoc": 50, "occupancy": 5},
    {"temperature": 22.0, "humidity": 45.0, "co2": 400, "pm25": 8.0, "pm10": 12.0, "tvoc": 30, "occupancy": 0},
    {"temperature": 24.0, "humidity": 55.0, "co2": 1200, "pm25": 40.0, "pm10": 60.0, "tvoc": 250, "occupancy": 30}
]

# Vérité terrain correspondante (0 = Activer, 1 = Désactiver)
# Déduite de vos commentaires
GROUND_TRUTH: List[int] = [
    0, # Conditions dégradées -> Activer
    0, # Température haute -> Activer
    1, # Conditions bonnes -> Désactiver
    0  # Conditions modérées/dégradées -> Activer
]

def run_simulation():
    """Exécute le scénario de test de bout en bout."""
    
    prediction_ids = []

    # --- ÉTAPE 1: FAIRE DES PRÉDICTIONS ---
    logging.info("--- DÉBUT DE LA SIMULATION : ÉTAPE 1 - PRÉDICTIONS ---")
    for i, data in enumerate(SAMPLE_TESTS):
        try:
            logging.info(f"Envoi de la requête de prédiction #{i+1}...")
            response = requests.post(PREDICT_ENDPOINT, json=data)
            
            if response.status_code == 200:
                result = response.json()
                prediction_id = result.get("prediction_id")
                prediction_ids.append(prediction_id)
                logging.info(f"  -> Succès ! Prédiction #{i+1}: {result}. ID: {prediction_id}")
            else:
                logging.error(f"  -> Échec de la prédiction #{i+1}. Statut: {response.status_code}, Réponse: {response.text}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"  -> Erreur réseau lors de la prédiction #{i+1}: {e}")
            logging.error("L'API n'est peut-être pas démarrée. Veuillez lancer 'docker-compose up' avant de lancer ce script.")
            return

        time.sleep(1) # Petite pause entre les requêtes

    if not prediction_ids:
        logging.error("Aucune prédiction n'a réussi. Arrêt de la simulation.")
        return

    # --- ÉTAPE 2: ENVOYER LA VÉRITÉ TERRAIN (FEEDBACK) ---
    logging.info("\n--- ÉTAPE 2 - ENVOI DU FEEDBACK (VÉRITÉ TERRAIN) ---")
    for i, prediction_id in enumerate(prediction_ids):
        feedback_data = {
            "prediction_id": prediction_id,
            "target": GROUND_TRUTH[i]
        }
        try:
            logging.info(f"Envoi du feedback pour la prédiction #{i+1} (ID: {prediction_id})...")
            response = requests.post(FEEDBACK_ENDPOINT, json=feedback_data)
            if response.status_code == 201:
                logging.info(f"  -> Succès ! Feedback pour la prédiction #{i+1} enregistré.")
            else:
                logging.error(f"  -> Échec de l'envoi du feedback. Statut: {response.status_code}, Réponse: {response.text}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"  -> Erreur réseau lors de l'envoi du feedback: {e}")
        
        time.sleep(1)

    # --- ÉTAPE 3: GÉNÉRER UNE ERREUR 404 ---
    logging.info("\n--- ÉTAPE 3 - GÉNÉRATION D'UNE ERREUR CLIENT (404) ---")
    try:
        requests.get(f"{API_BASE_URL}/ceci-est-une-fausse-url")
        logging.info("Appel vers une URL inexistante effectué pour tester le monitoring d'erreurs.")
    except Exception as e:
        logging.warning(f"Erreur (attendue) lors de l'appel 404: {e}")

    # --- ÉTAPE 4: DÉCLENCHER LES RAPPORTS EVIDENTLY ---
    logging.info("\n--- ÉTAPE 4 - MISE À JOUR DES RAPPORTS EVIDENTLY ---")
    logging.info("Cette étape peut prendre quelques secondes...")
    try:
        response = requests.post(UPDATE_REPORTS_ENDPOINT)
        if response.status_code == 200:
            logging.info("  -> Succès ! Les rapports et les métriques (Drift, Accuracy) ont été mis à jour.")
        else:
            logging.error(f"  -> Échec de la mise à jour des rapports. Statut: {response.status_code}, Réponse: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"  -> Erreur réseau lors de la mise à jour des rapports: {e}")
    
    logging.info("\n--- SIMULATION TERMINÉE ---")
    logging.info("Vous devriez maintenant voir des données apparaître dans TOUS les panneaux de votre tableau de bord Grafana.")
    logging.info("Note: Les données peuvent prendre 1 à 2 minutes pour être complètement visibles à cause des intervalles de rafraîchissement.")

if __name__ == "__main__":
    run_simulation()
