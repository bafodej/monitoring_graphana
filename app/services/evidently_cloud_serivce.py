import os
from dotenv import load_dotenv
import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

class EvidentlyCloudService:
    """
    Service pour envoyer les métriques à Evidently Cloud
    """
    
    def __init__(self):
        self.api_token = os.getenv('EVIDENTLY_API_TOKEN')
        self.project_id = os.getenv('EVIDENTLY_PROJECT_ID')
        self.workspace_id = os.getenv('EVIDENTLY_WORKSPACE_ID')
        
        if not all([self.api_token, self.project_id, self.workspace_id]):
            logger.warning(" Evidently Cloud non configuré (variables manquantes)")
            self.connected = False
            return
        
        self.connected = True
        logger.info(" Configuration Evidently Cloud chargée")
        logger.info(f"   Workspace ID: {self.workspace_id}")
        logger.info(f"   Project ID: {self.project_id}")
    
    def send_prediction_data(
        self,
        input_data: Dict[str, float],
        prediction_result: Dict[str, Any]
    ):
        """
        Envoie une prédiction à Evidently Cloud
        """
        if not self.connected:
            logger.debug("Evidently Cloud non configuré, skip")
            return
        
        try:
            # Créer un DataFrame avec les données
            data = {
                **input_data,
                'prediction': prediction_result['prediction'],
                'action': prediction_result['action']
            }
            df = pd.DataFrame([data])
            
            # Pour Evidently 0.7.16, on va envoyer via l'API REST
            # TODO: Implémenter l'envoi via requests
            logger.debug(f" Prédiction prête pour Evidently Cloud")
            
            # NOTE: L'envoi réel nécessite l'API REST d'Evidently
            # Cela sera implémenté dans la prochaine étape
            
        except Exception as e:
            logger.error(f" Erreur envoi Evidently Cloud: {e}")
    
    def is_connected(self) -> bool:
        """
        Vérifie si la connexion est configurée
        """
        return self.connected

# Instance globale
evidently_service = EvidentlyCloudService()