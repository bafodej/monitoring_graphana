import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent # Ceci pointe vers le dossier /app

class AppConfig:
    """
    Configuration centralisée de l'application.
    Tous les chemins sont définis ici pour une gestion facile.
    """
    # --- Chemins du Modèle ---
    MODEL_DIR = BASE_DIR / "data"
    MODEL_PATH = MODEL_DIR / "indoor_aqi_model.pkl"
    MODEL_VERSION_PATH = MODEL_DIR / "version.txt"
    REFERENCE_DATA_PATH = MODEL_DIR / "reference_data.csv"

    # --- Chemins des Rapports et Logs ---
    REPORTS_DIR = BASE_DIR / "reports"
    PREDICTION_LOG_PATH = REPORTS_DIR / "prediction_data.csv"
    GROUND_TRUTH_LOG_PATH = REPORTS_DIR / "ground_truth.csv"
    METRICS_CACHE_PATH = REPORTS_DIR / "metrics_cache.json"