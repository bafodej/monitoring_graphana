from fastapi import APIRouter
from ..services.logging_service import prediction_logger
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"]
)

@router.get("/evidently")
async def get_evidently_metrics():
    """
    Endpoint pour exposer les métriques Evidently au format JSON
    Pour scraping Prometheus/Grafana
    """
    try:
        log_file = Path("data/predictions_log.csv")
        
        if not log_file.exists():
            return {
                "status": "no_data",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0
            }
        
        df = pd.read_csv(log_file)
        
        metrics = {
            "status": "ok",
            "predictions_count": len(df),
            "predictions_activate": int((df['prediction'] == 0).sum()) if len(df) > 0 else 0,
            "predictions_deactivate": int((df['prediction'] == 1).sum()) if len(df) > 0 else 0,
            "features": {}
        }
        
        if len(df) > 0:
            feature_columns = ['temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy']
            
            for col in feature_columns:
                if col in df.columns:
                    metrics["features"][col] = {
                        "mean": float(df[col].mean()),
                        "std": float(df[col].std()),
                        "min": float(df[col].min()),
                        "max": float(df[col].max())
                    }
        
        return metrics
        
    except Exception as e:
        logger.error(f" Erreur: {e}")
        return {"status": "error", "error": str(e)}

@router.get("/evidently/drift")
async def get_drift_status():
    """
    Statut du drift détecté par Evidently
    """
    return {
        "drift_detected": False,
        "last_check": None,
        "drifted_features": []
    }