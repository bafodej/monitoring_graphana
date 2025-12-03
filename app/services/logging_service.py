import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging
import numpy as np
from ..config import AppConfig

logger = logging.getLogger(__name__)

class PredictionLogger:
    """
    Service pour logger les prédictions dans un fichier CSV pour Evidently.
    """
    
    def __init__(self, log_file_path: Path):
        self._log_file = log_file_path
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
            'action',
            'probability'
        ]
        
    def initialize_log_file(self):
        try:
            self._log_file.parent.mkdir(parents=True, exist_ok=True)
            if not self._log_file.exists():
                df = pd.DataFrame(columns=self.columns)
                df.to_csv(self._log_file, index=False)
                logger.info(f"Fichier de log créé: {self._log_file}")
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
                'temperature': self._clean_value(input_data.get('temperature')),
                'humidity': self._clean_value(input_data.get('humidity')),
                'co2': self._clean_value(input_data.get('co2')),
                'pm25': self._clean_value(input_data.get('pm25')),
                'pm10': self._clean_value(input_data.get('pm10')),
                'tvoc': self._clean_value(input_data.get('tvoc')),
                'occupancy': self._clean_value(input_data.get('occupancy')),
                'prediction': self._clean_value(prediction_result.get('prediction')),
                'action': prediction_result.get('action'),
                'probability': self._clean_value(prediction_result.get('probability'))
            }
            
            df = pd.DataFrame([log_entry])
            df = pd.DataFrame([log_entry], columns=self.columns)
            df.to_csv(self._log_file, mode='a', header=False, index=False)
            
        except Exception as e:
            logger.error(f"Erreur lors du logging: {e}")

# --------------------------------------------------------
# 🟩 Instance globale accessible par les routes FastAPI
# --------------------------------------------------------
prediction_logger = PredictionLogger(log_file_path=AppConfig.PREDICTION_LOG_FILE)
