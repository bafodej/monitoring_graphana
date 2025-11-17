from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AirQualityInput(BaseModel):
    """
    Schéma pour les données d'entrée des capteurs IoT
    """
    temperature: float = Field(..., description="Température en °C", ge=-20, le=50)
    humidity: float = Field(..., description="Humidité relative en %", ge=0, le=100)
    co2: float = Field(..., description="Concentration de CO2 en ppm", ge=0)
    tvoc: float = Field(..., description="Composés organiques volatils totaux en ppb", ge=0)
    pm25: float = Field(..., description="Particules fines PM2.5 en µg/m³", ge=0)
    pm10: float = Field(..., description="Particules PM10 en µg/m³", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 22.5,
                "humidity": 45.0,
                "co2": 450.0,
                "tvoc": 150.0,
                "pm25": 12.5,
                "pm10": 20.0
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
                "action": "Activer",
                "prediction": 1,
                "confidence": 0.85,
                "probability_activate": 0.85,
                "probability_deactivate": 0.15,
                "timestamp": "2025-11-17T14:30:00"
            }
        }