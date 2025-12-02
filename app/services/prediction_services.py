import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class AirQualityPredictionService:
    """
    Service pour gérer les prédictions de qualité d'air.
    """

    def __init__(self, model_path: str = "app/data/indoor_aqi_model.pkl", model_version: str = "1.0.0"):
        self.model_path = Path(model_path)
        self.model = None
        self.model_version = model_version
        self.feature_names = [
            'temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy'
        ]

    def load_model(self) -> bool:
        try:
            if not self.model_path.exists():
                logger.warning(f"Modèle non trouvé: {self.model_path}")
                return False

            self.model = joblib.load(self.model_path)
            logger.info(f"Modèle chargé depuis {self.model_path} (version: {self.model_version})")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            return False

    def predict(self, features: Dict[str, float]) -> int:
        """
        Fait une prédiction binaire simple (1 = Good, 0 = Moderate/Poor).
        """
        binary_pred, _ = self.predict_with_proba(features)
        return binary_pred

    def predict_with_proba(self, features: Dict[str, float]) -> Tuple[int, float]:
        """
        Fait une prédiction et retourne la classe binaire ainsi que la probabilité de confiance.
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")

        # Créer un DataFrame à partir des features
        X = pd.DataFrame([features], columns=self.feature_names)

        # Prédiction des probabilités et de la classe
        probabilities = self.model.predict_proba(X)[0]
        label_index = np.argmax(probabilities)
        confidence = probabilities[label_index]
        label = self.model.classes_[label_index]

        # Convertir le label texte en binaire
        label_to_binary = {"Good": 1, "Moderate": 0, "Poor": 0}
        binary_prediction = label_to_binary.get(label, 0)

        return binary_prediction, float(confidence)


    def is_loaded(self) -> bool:
        return self.model is not None

    def get_model_version(self) -> str:
        return self.model_version


# Instance unique du service
prediction_service = AirQualityPredictionService()
