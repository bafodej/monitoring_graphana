import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent # Ceci pointe vers le dossier /code

class AppConfig:
    """
    Configuration centralisée de l'application.
    """
    # Configuration du modèle
    MODEL_DIR = BASE_DIR / "data"
    MODEL_PATH = MODEL_DIR / "indoor_aqi_model.pkl"
    MODEL_VERSION_PATH = MODEL_DIR / "version.txt"

    # Configuration du logging pour Evidently
    LOGS_DIR = BASE_DIR / "reports"
    PREDICTION_LOG_FILE = LOGS_DIR / "prediction_data.csv"