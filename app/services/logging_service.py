import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PredictionLogger:
    """
    Service pour logger les prédictions dans un fichier CSV pour Evidently AI
    """
    
    def __init__(self, log_path: str = "app/data/predictions_log.csv"):
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
        """
        Initialise le fichier CSV s'il n'existe pas
        """
        try:
            if not self.log_path.exists():
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                df = pd.DataFrame(columns=self.columns)
                df.to_csv(self.log_path, index=False)
                logger.info(f"Fichier de log créé: {self.log_path}")
            else:
                logger.info(f"Fichier de log existant: {self.log_path}")
        except Exception as e:
            logger.error(f"Erreur initialisation log: {e}")
    
    def log_prediction(
        self, 
        input_data: Dict[str, float], 
        prediction_result: Dict[str, Any]
    ): 
        """
        Enregistre une prédiction dans le CSV
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'temperature': input_data['temperature'],
                'humidity': input_data['humidity'],
                'co2': input_data['co2'],
                'pm25': input_data['pm25'],
                'pm10': input_data['pm10'],
                'tvoc': input_data['tvoc'],
                'occupancy': input_data['occupancy'],
                'prediction': prediction_result['prediction'],
                'action': prediction_result['action']
            }
            
            df = pd.DataFrame([log_entry])
            df.to_csv(self.log_path, mode='a', header=False, index=False)
            
            logger.debug(f"Prédiction loggée: {prediction_result['action']}")
            
        except Exception as e:
            logger.error(f"Erreur lors du logging: {e}")
    
    def get_predictions_count(self) -> int:
        if not self.log_path.exists():
            return 0
        try:
            df = pd.read_csv(self.log_path)
            return len(df)
        except:
            return 0
    
    def get_recent_predictions(self, n: int = 100) -> pd.DataFrame:
        if not self.log_path.exists():
            return pd.DataFrame()
        try:
            df = pd.read_csv(self.log_path)
            return df.tail(n)
        except Exception as e:
            logger.error(f"Erreur lecture prédictions: {e}")
            return pd.DataFrame()
    
    def get_all_predictions(self) -> pd.DataFrame:
        if not self.log_path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(self.log_path)
        except Exception as e:
            logger.error(f"Erreur lecture prédictions: {e}")
            return pd.DataFrame()

prediction_logger = PredictionLogger()
