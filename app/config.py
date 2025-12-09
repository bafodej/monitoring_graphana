from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field

class AppConfig(BaseSettings):
    """
    Configuration centralisée de l'application.
    """

    # Répertoire racine du projet (automatique)
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1])

    # --- Dossiers / fichiers du modèle ---
    MODEL_DIR: Path = None
    MODEL_PATH: Path = None
    MODEL_VERSION_PATH: Path = None
    REFERENCE_DATA_PATH: Path = None

    # --- Logs, monitoring et rapports ---
    REPORTS_DIR: Path = None
    PREDICTION_LOG_PATH: Path = None
    GROUND_TRUTH_LOG_PATH: Path = None
    METRICS_CACHE_PATH: Path = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **values):
        super().__init__(**values)

        # Construction dynamique des chemins
        self.MODEL_DIR = self.BASE_DIR / "app" / "data"
        self.MODEL_PATH = self.MODEL_DIR / "indoor_aqi_model.pkl"
        self.MODEL_VERSION_PATH = self.MODEL_DIR / "version.txt"
        self.REFERENCE_DATA_PATH = self.MODEL_DIR / "reference_data.csv"

        self.REPORTS_DIR = self.BASE_DIR / "reports"
        self.PREDICTION_LOG_PATH = self.REPORTS_DIR / "prediction_data.csv"
        self.GROUND_TRUTH_LOG_PATH = self.REPORTS_DIR / "ground_truth.csv"
        self.METRICS_CACHE_PATH = self.REPORTS_DIR / "metrics_cache.json"


# Instance cachée pour éviter de recréer AppConfig à chaque accès
@lru_cache()
def get_settings() -> AppConfig:
    return AppConfig()
