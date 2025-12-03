import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging
import pandas as pd
from .config import AppConfig

logger = logging.getLogger(__name__)

class AirQualityPredictionService:
    """
    Service pour gérer les prédictions de qualité d'air.
    """

    def __init__(self):
        self._model_path = AppConfig.MODEL_PATH
        self._version_path = AppConfig.MODEL_VERSION_PATH
        self.model = None
        self.model_version = "unknown"

    def load_model(self) -> bool:
        try:
            if not self._model_path.exists():
                logger.error(f"Fichier du modèle non trouvé à l'emplacement: {self._model_path}")
                return False

            self.model = joblib.load(self._model_path)
            logger.info(f"Modèle chargé depuis: {self._model_path}")

            if self._version_path.exists():
                self.model_version = self._version_path.read_text().strip()
                logger.info(f"Version du modèle: {self.model_version}")
            else:
                logger.warning(f"Fichier de version non trouvé à l'emplacement: {self._version_path}")
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

        feature_names = self.model.feature_names_in_
        # Créer un DataFrame à partir des features
        X = pd.DataFrame([features], columns=feature_names)

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
