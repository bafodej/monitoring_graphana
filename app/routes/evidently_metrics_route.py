from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..services.logging_service import prediction_logger
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from ..metrics import generate_classification_report, generate_drift_report # Import the report generation functions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Metrics"])

REFERENCE_DATA_PATH = Path("app/data/reference_data.csv")
PREDICTION_LOG_PATH = Path("app/reports/prediction_data.csv")

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
        if not PREDICTION_LOG_PATH.exists():
            return JSONResponse({
                "status": "no_data",
                "predictions_count": 0,
                "predictions_activate": 0,
                "predictions_deactivate": 0,
                "features": {}
            })

        df = pd.read_csv(PREDICTION_LOG_PATH)

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

@router.post("/evidently/update-reports") # Changed to POST as it modifies state (metrics)
async def update_evidently_reports():
    """
    Déclenche la génération des rapports Evidently pour la dérive des données
    et la performance du modèle, et met à jour les métriques Prometheus.
    """
    try:
        if not REFERENCE_DATA_PATH.exists():
            raise HTTPException(status_code=404, detail=f"Fichier de données de référence introuvable: {REFERENCE_DATA_PATH}")
        if not PREDICTION_LOG_PATH.exists():
            raise HTTPException(status_code=404, detail=f"Fichier de log de prédictions introuvable: {PREDICTION_LOG_PATH}")

        reference_df = pd.read_csv(REFERENCE_DATA_PATH)
        current_df = pd.read_csv(PREDICTION_LOG_PATH)

        feature_cols = [
            'temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy'
        ]
        # Ensure only relevant feature columns are used for drift and classification
        reference_df_features = reference_df[feature_cols]
        current_df_features = current_df[feature_cols]
        
        # For classification report, we also need 'target' and 'prediction' columns if they exist
        # Assuming 'prediction' is the model's output and 'target' is the ground truth
        # For this example, let's assume 'prediction' from the log is the target for accuracy.
        # This part might need adjustment based on how true labels are handled.
        # If 'target' is available in current_df for evaluating accuracy, it should be used.
        # IMPORTANT: Currently, 'prediction' is used as 'target' for simplicity in this example.
        # For a truly meaningful accuracy metric, the actual ground truth ('target')
        # should be logged alongside the predictions in `prediction_data.csv`.
        # This architectural change is beyond the scope of this fix.


        # To make generate_classification_report work, we need 'prediction' and 'target' columns
        # Adding dummy 'target' column for now, assuming 'prediction' is the model's output.
        # In a real scenario, you'd have actual ground truth.
        current_df_for_classification = current_df.copy()
        if 'prediction' in current_df_for_classification.columns:
            # Assuming 'prediction' column from current_df acts as target for simplicity
            # In a real-world scenario, you'd have a 'target' column with ground truth
            current_df_for_classification['target'] = current_df_for_classification['prediction']
        else:
            current_df_for_classification['prediction'] = 0 # Dummy prediction
            current_df_for_classification['target'] = 0 # Dummy target

        # Prepare reference_df for classification report (needs 'prediction' and 'target')
        reference_df_for_classification = reference_df.copy()
        # Assuming we need to simulate 'prediction' and 'target' in reference data for Evidently's ClassificationPreset
        if 'prediction' not in reference_df_for_classification.columns:
            reference_df_for_classification['prediction'] = 0
        if 'target' not in reference_df_for_classification.columns:
            reference_df_for_classification['target'] = 0
        
        # Generate Data Drift Report
        generate_drift_report(
            reference_data=reference_df_features,
            current_data=current_df_features,
            output_path=Path("reports/data_drift_report.html")
        )

        # Generate Classification Performance Report
        # Ensure 'prediction' and 'target' columns are present for Evidently
        generate_classification_report(
            reference_data=reference_df_for_classification,
            current_data=current_df_for_classification,
            model_version="v1.0", # Assuming model version "v1.0"
            output_path=Path("reports/classification_report.html") # New output path
        )

        return JSONResponse({"status": "ok", "message": "Evidently reports generated and metrics updated successfully."})

    except HTTPException as he:
        logger.error(f"Erreur lors de la mise à jour des rapports Evidently: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la mise à jour des rapports Evidently: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur lors de la génération des rapports: {e}")

