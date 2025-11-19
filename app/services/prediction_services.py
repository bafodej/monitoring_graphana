import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class AirQualityPredictionService:
    """
    Service pour gérer les prédictions de qualité d'air.
    """

    def __init__(self, model_path: str = "app/data/indoor_aqi_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_names = [
            'temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy'
        ]

    def load_model(self) -> bool:
        try:
            if not self.model_path.exists():
                logger.warning(f"Modèle non trouvé: {self.model_path}")
                return False

            self.model = joblib.load(self.model_path)
            logger.info(f"Modèle chargé depuis {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            return False

    def predict(self, features: Dict[str, float]) -> int:
        """
        Fait une prédiction binaire pour l'API (1 = Good, 0 = Moderate/Poor)
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
    
        X = pd.DataFrame([{
            'temperature': features['temperature'],
            'humidity': features['humidity'],
            'co2': features['co2'],
            'pm25': features['pm25'],
            'pm10': features['pm10'],
            'tvoc': features['tvoc'],
            'occupancy': features['occupancy']
        }])
    
        # Prédiction label
        label = self.model.predict(X)[0]  # "Good", "Moderate", "Poor"
    
        # Convertir en 0/1 pour l'API
        label_to_binary = {"Good": 1, "Moderate": 0, "Poor": 0}
        binary_prediction = label_to_binary.get(label, 0)
    
        return binary_prediction



    def is_loaded(self) -> bool:
        return self.model is not None


# Instance unique du service
prediction_service = AirQualityPredictionService()