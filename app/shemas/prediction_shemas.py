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

    prediction: int = Field(..., description="1 = Désactiver, 0 = Activer")

    
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
