from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..services.logging_service import prediction_logger
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def clean_value(v):
    """Convertit NaN / inf / none en valeur JSON-safe"""
    if v is None:
        return 0
    if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
        return 0
    return float(v)


@router.get("/evidently")
async def get_evidently_metrics():
    try:
        log_file = Path("data/predictions_log.csv")

        if not log_file.exists():
            return JSONResponse({
                "status": "no_data",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0,
                "features": {}
            })

        df = pd.read_csv(log_file)

        metrics = {
            "status": "ok",
            "predictions_count": clean_value(len(df)),
            "predictions_activate": clean_value((df['prediction'] == 0).sum()),
            "predictions_deactivate": clean_value((df['prediction'] == 1).sum()),
            "features": {}
        }

        feature_cols = [
            'temperature', 'humidity', 'co2',
            'pm25', 'pm10', 'tvoc', 'occupancy'
        ]

        if len(df) > 0:
            for col in feature_cols:
                if col in df.columns:
                    metrics["features"][col] = {
                        "mean": clean_value(df[col].mean()),
                        "std": clean_value(df[col].std()),
                        "min": clean_value(df[col].min()),
                        "max": clean_value(df[col].max())
                    }

        return JSONResponse(metrics)

    except Exception as e:
        logger.error(f"Erreur Evidently: {e}")
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)
