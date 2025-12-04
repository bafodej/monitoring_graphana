from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json

from ..metrics import generate_classification_report, generate_drift_report
from ..config import AppConfig  # Importer la configuration centralisée

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
    """
    Retourne les métriques de prédiction depuis un cache.
    Ce cache est mis à jour par l'endpoint POST /evidently/update-reports.
    """
    try:
        if not AppConfig.METRICS_CACHE_PATH.exists():
            return JSONResponse({
                "status": "no_data",
                "message": "Le cache de métriques est vide. Déclenchez une mise à jour via POST /metrics/evidently/update-reports.",
                "predictions_count": 0, "predictions_activate": 0, "predictions_deactivate": 0, "features": {}
            })

        with open(AppConfig.METRICS_CACHE_PATH, 'r') as f:
            metrics = json.load(f)
        
        return JSONResponse(metrics)

    except Exception as e:
        logger.error(f"Erreur lors de la lecture du cache de métriques Evidently: {e}")
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

@router.post("/evidently/update-reports")
async def update_evidently_reports():
    """
    Déclenche la génération des rapports Evidently et met à jour le cache de métriques JSON.
    """
    try:
        # --- Vérification et chargement des données ---
        if not AppConfig.REFERENCE_DATA_PATH.exists():
            raise HTTPException(status_code=404, detail=f"Fichier de données de référence introuvable: {AppConfig.REFERENCE_DATA_PATH}")
        if not AppConfig.PREDICTION_LOG_PATH.exists():
            raise HTTPException(status_code=404, detail=f"Fichier de log de prédictions introuvable: {AppConfig.PREDICTION_LOG_PATH}")

        reference_df = pd.read_csv(AppConfig.REFERENCE_DATA_PATH)
        current_predictions_df = pd.read_csv(AppConfig.PREDICTION_LOG_PATH)

        feature_cols = ['temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy']
        
        # --- 1. Mise à jour du cache de métriques (nouvelle étape) ---
        metrics_to_cache = {
            "status": "ok",
            "predictions_count": clean_value(len(current_predictions_df)),
            "predictions_activate": clean_value((current_predictions_df['prediction'] == 0).sum()),
            "predictions_deactivate": clean_value((current_predictions_df['prediction'] == 1).sum()),
            "features": {}
        }
        if len(current_predictions_df) > 0:
            for col in feature_cols:
                if col in current_predictions_df.columns:
                    metrics_to_cache["features"][col] = {
                        "mean": clean_value(current_predictions_df[col].mean()),
                        "std": clean_value(current_predictions_df[col].std()),
                        "min": clean_value(current_predictions_df[col].min()),
                        "max": clean_value(current_predictions_df[col].max())
                    }
        
        AppConfig.METRICS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(AppConfig.METRICS_CACHE_PATH, 'w') as f:
            json.dump(metrics_to_cache, f, indent=4)
        logger.info(f"Cache de métriques mis à jour: {AppConfig.METRICS_CACHE_PATH}")

        # --- 2. Génération du Rapport de Dérive des Données ---
        generate_drift_report(
            reference_data=reference_df[feature_cols],
            current_data=current_predictions_df[feature_cols],
            output_path=AppConfig.REPORTS_DIR / "data_drift_report.html"
        )
        logger.info("Rapport de dérive des données généré.")

        # --- 3. Génération du Rapport de Performance ---
        report_message = "Rapports Evidently (dérive et performance) et cache de métriques générés avec succès."
        
        if not AppConfig.GROUND_TRUTH_LOG_PATH.exists() or pd.read_csv(AppConfig.GROUND_TRUTH_LOG_PATH).empty:
            logger.warning("Fichier de vérité terrain introuvable ou vide. Le rapport de performance est ignoré.")
            report_message = "Cache et rapport de dérive générés, mais rapport de performance ignoré (pas de vérité terrain)."
        else:
            ground_truth_df = pd.read_csv(AppConfig.GROUND_TRUTH_LOG_PATH)
            merged_df = pd.merge(current_predictions_df, ground_truth_df, on="prediction_id")

            if merged_df.empty:
                logger.warning("Aucune prédiction ne correspond à la vérité terrain. Le rapport de performance est ignoré.")
                report_message = "Cache et rapport de dérive générés, mais rapport de performance ignoré (aucune correspondance de vérité terrain)."
            else:
                reference_for_classification = reference_df.copy()
                if 'target' not in reference_for_classification.columns:
                    reference_for_classification['target'] = 0
                    reference_for_classification['prediction'] = 0

                generate_classification_report(
                    reference_data=reference_for_classification,
                    current_data=merged_df,
                    model_version="v1.0",
                    output_path=AppConfig.REPORTS_DIR / "classification_report.html"
                )
                logger.info("Rapport de performance de classification généré avec la vérité terrain.")

        return JSONResponse({"status": "ok", "message": report_message})

    except HTTPException as he:
        logger.error(f"Erreur lors de la mise à jour des rapports Evidently: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la mise à jour des rapports Evidently: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {e}")
