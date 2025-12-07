from pathlib import Path
import os

class AppConfig:
    """
    Configuration centralisée de l'application.
    Tous les chemins sont définis ici pour une gestion facile.
    Compatible avec Docker.
    """
    # Base directory dans le container
    BASE_DIR = Path("/home/appuser/code")

    # --- Chemins du Modèle ---
    MODEL_DIR = BASE_DIR / "app" / "data"
    MODEL_PATH = MODEL_DIR / "indoor_aqi_model.pkl"
    MODEL_VERSION_PATH = MODEL_DIR / "version.txt"
    REFERENCE_DATA_PATH = MODEL_DIR / "reference_data.csv"

    # --- Chemins des Rapports et Logs ---
    REPORTS_DIR = BASE_DIR / "reports"
    PREDICTION_LOG_PATH = REPORTS_DIR / "prediction_data.csv"
    GROUND_TRUTH_LOG_PATH = REPORTS_DIR / "ground_truth.csv"
    METRICS_CACHE_PATH = REPORTS_DIR / "metrics_cache.json"
