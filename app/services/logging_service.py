import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)

class PredictionLogger:
    """
    Service pour logger les prédictions dans un fichier CSV pour Evidently AI
    """
    
    def __init__(self, log_path: str = "data/predictions_log.csv"):
        self.log_path = Path(log_path)
        self.columns = [
            'timestamp',
            'temperature',
            'humidity',
            'co2',
            'pm25',
            'pm10',
            'tvoc',
            'occupancy',
            'prediction',
            'action'
        ]
        
    def initialize_log_file(self):
        try:
            if not self.log_path.exists():
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                df = pd.DataFrame(columns=self.columns)
                df.to_csv(self.log_path, index=False)
                logger.info(f"Fichier de log créé: {self.log_path}")
        except Exception as e:
            logger.error(f"Erreur initialisation log: {e}")
    
    def _clean_value(self, v):
        """Supprime NaN, inf, None → remplace par 0"""
        if v is None:
            return 0
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            return 0
        return v
    
    def log_prediction(self, input_data: Dict[str, float], prediction_result: Dict[str, Any]):
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'temperature': self._clean_value(input_data['temperature']),
                'humidity': self._clean_value(input_data['humidity']),
                'co2': self._clean_value(input_data['co2']),
                'pm25': self._clean_value(input_data['pm25']),
                'pm10': self._clean_value(input_data['pm10']),
                'tvoc': self._clean_value(input_data['tvoc']),
                'occupancy': self._clean_value(input_data['occupancy']),
                'prediction': self._clean_value(prediction_result['prediction']),
                'action': prediction_result['action']
            }
            
            df = pd.DataFrame([log_entry])
            df.to_csv(self.log_path, mode='a', header=False, index=False)
            
        except Exception as e:
            logger.error(f"Erreur lors du logging: {e}")

# --------------------------------------------------------
# 🟩 Instance globale accessible par les routes FastAPI
# --------------------------------------------------------
prediction_logger = PredictionLogger()
prediction_logger.initialize_log_file()
