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
    MODEL_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "app" / "data")
    MODEL_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "app" / "data" / "indoor_aqi_model.pkl")
    MODEL_VERSION_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "app" / "data" / "version.txt")
    REFERENCE_DATA_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "app" / "data" / "reference_data.csv")

    # --- Logs, monitoring et rapports ---
    REPORTS_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "reports")
    PREDICTION_LOG_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "reports" / "prediction_data.csv")
    GROUND_TRUTH_LOG_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "reports" / "ground_truth.csv")
    METRICS_CACHE_PATH: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[1] / "reports" / "metrics_cache.json")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance cachée pour éviter de recréer AppConfig à chaque accès
@lru_cache()
def get_settings() -> AppConfig:
    return AppConfig()
