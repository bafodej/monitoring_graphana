from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AirQualityInput(BaseModel):
    """
    Schéma pour les données d'entrée des capteurs IoT
    """
    co2: float = Field(..., description="Concentration de CO2 en ppm", ge=0)
    tvoc: float = Field(..., description="Composés organiques volatils totaux en ppb", ge=0)
    pm25: float = Field(..., description="Particules fines PM2.5 en µg/m³", ge=0)
    pm10: float = Field(..., description="Particules PM10 en µg/m³", ge=0)
    co: float = Field(..., description="Particules de monoxyde de carbone  en ppm", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "co2": 1200,
                "tvoc": 200,
                "pm25": 45.0,
                "pm10": 80.0,
                "co": 2.1,
            }
        }

class PredictionOutput(BaseModel):
    """
    Schéma pour la réponse de prédiction
    """
    action: str = Field(..., description="Action recommandée : 'Activer' ou 'Désactiver'")
    prediction: int = Field(..., description="0 = Désactiver, 1 = Activer")
    confidence: float = Field(..., description="Confiance de la prédiction (0-1)")
    probability_activate: float = Field(..., description="Probabilité d'activation")
    probability_deactivate: float = Field(..., description="Probabilité de désactivation")
    timestamp: str = Field(..., description="Horodatage de la prédiction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "co2": 1200,
                "tvoc": 200,
                "pm25": 45.0,
                "pm10": 80.0,
                "co": 2.1,
            }
        }

