from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AirQualityInput(BaseModel):
    """
    Schéma pour les données d'entrée des capteurs IoT
    """
    temperature: float = Field(..., description="temperature de la piece en °", ge=0)
    humidity: float = Field(..., description="humiditée de la piece en %",ge=0)
    co2: float = Field(..., description="Concentration de CO2 en ppm", ge=0)
    pm25: float = Field(..., description="Particules fines PM2.5 en µg/m³", ge=0)
    pm10: float = Field(..., description="Particules PM10 en µg/m³", ge=0)
    tvoc: float = Field(..., description="Composés organiques volatils totaux en ppb", ge=0)
    occupancy: float = Field(..., description="Nombre d'occupant dans la piece", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 25.3,
                "humidity": 61.2,
                "co2": 1200,
                "pm25": 45.0,
                "pm10": 80.0,
                "tvoc": 200,
                "occupancy": 10
            }
        }

class PredictionOutput(BaseModel):
    """
    Schéma pour la réponse de prédiction
    """
    prediction_id: str = Field(..., description="Identifiant unique de la prédiction")
    prediction: int = Field(..., description="Résultat de la prédiction binaire (1 = Désactiver, 0 = Activer)")
    confidence: float = Field(..., description="Probabilité de confiance de la prédiction (entre 0.0 et 1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "prediction": 0,
                "confidence": 0.95
            }
        }

class FeedbackInput(BaseModel):
    """
    Schéma pour la soumission de la vérité terrain (ground truth).
    """
    prediction_id: str = Field(..., description="L'identifiant de la prédiction à laquelle ce feedback se rapporte.")
    target: int = Field(..., description="La vraie valeur (vérité terrain). 0 pour 'Activer', 1 pour 'Désactiver'.")

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "target": 0
            }
        }
