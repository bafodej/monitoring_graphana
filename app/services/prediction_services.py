import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AirQualityPredictionService:
    """
    Service pour gérer les prédictions de qualité d'air
    """
    
    def __init__(self, model_path: str = "data/indoor_aqi_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_names = [
            'temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy'
        ]
        
    def load_model(self) -> bool:
        """
        Charge le modèle depuis le fichier
        """
        try:
            if not self.model_path.exists():
                logger.warning(f" Modèle non trouvé: {self.model_path}")
                return False
            
            self.model = joblib.load(self.model_path)
            logger.info(f" Modèle chargé depuis {self.model_path}")
            logger.info(f"   Type: {type(self.model).__name__}")
            logger.info(f"   Features attendues: {self.feature_names}")
            
            return True
            
        except Exception as e:
            logger.error(f" Erreur lors du chargement du modèle: {e}")
            return False
    
    def predict(self, features: Dict[str, float]) -> Tuple[int, np.ndarray, float]:
        """
        Fait une prédiction
        
        Args:
            features: Dictionnaire des features
            
        Returns:
            Tuple (prédiction, probabilités, confiance)
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        # Préparer les features dans le bon ordre
        X = np.array([
            features['temperature'],
            features['humidity'],
            features['co2'],
            features['pm25'],
            features['pm10'],
            features['tvoc'],
            features['occupancy']
        ]).reshape(1, -1)
        
        # Prédiction
        prediction = int(self.model.predict(X)[0])
        probabilities = self.model.predict_proba(X)[0]
        confidence = float(max(probabilities))
        
        return prediction, probabilities, confidence
    
    def is_loaded(self) -> bool:
        """
        Vérifie si le modèle est chargé
        """
        return self.model is not None

# Instance globale du service
prediction_service = AirQualityPredictionService()