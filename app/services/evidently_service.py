from pathlib import Path
from typing import Dict, Optional
import logging

import pandas as pd
import pandas.errors
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset

from ..metrics import (
    ml_data_drift_score,
    ml_feature_drift_detected,
    ml_model_accuracy,
    ml_model_f1,
    record_api_error
)
from ..config import get_settings

# import du service de prédiction sans créer de circular import
from .prediction_services import prediction_service

logger = logging.getLogger(__name__)


class EvidentlyService:
    """
    Service dédié à la génération des rapports Evidently :
    - Data Drift
    - Classification Performance
    - Mise à jour des métriques Prometheus
    """

    # -------------------------------------------------------------------------
    # ------------------------- METRICS UPDATES ------------------------------
    # -------------------------------------------------------------------------
    def _update_drift_metrics(self, drift_results: dict) -> None:
        """Met à jour les métriques Prometheus liées à la dérive."""
        try:
            metrics = drift_results.get("metrics", [])
            for metric in metrics:
                if metric.get("metric") == "DatasetDriftMetric":
                    result = metric.get("result", {})

                    drift_score = result.get("dataset_drift_score", 0.0)
                    ml_data_drift_score.set(drift_score)

                    drift_by_cols = result.get("drift_by_columns", {})
                    for feature, feature_drift in drift_by_cols.items():
                        if feature_drift.get("drift_detected", False):
                            ml_feature_drift_detected.labels(feature_name=feature).inc()

                    logger.info(f"[DRIFT] Score de dérive mis à jour : {drift_score:.3f}")
                    break
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques de drift : {e}")
            record_api_error("drift_metrics_update")

    def _update_model_performance_metrics(self, model_version: str, performance: Dict[str, float]) -> None:
        """Met à jour accuracy et F1-score."""
        try:
            accuracy = performance.get("accuracy")
            f1 = performance.get("f1")

            if accuracy is not None:
                ml_model_accuracy.labels(model_version=model_version).set(accuracy)
            if f1 is not None:
                ml_model_f1.labels(model_version=model_version).set(f1)

            logger.info(f"[MODEL PERF] v{model_version} | accuracy={accuracy:.3f}, f1={f1:.3f}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques modèle : {e}")
            record_api_error("performance_metrics_update")

    # -------------------------------------------------------------------------
    # ------------------------------ REPORTS ---------------------------------
    # -------------------------------------------------------------------------
    def generate_classification_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        model_version: str = "v1.0",
        output_path: Optional[Path] = None
    ) -> Dict:
        """Génère un rapport de classification Evidently + met à jour les métriques."""
        try:
            logger.info("Génération du rapport Evidently : Classification...")
            report = Report(metrics=[ClassificationPreset()])
            report.run(reference_data=reference_data, current_data=current_data)

            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                report.save_html(str(output_path))
                logger.info(f"Rapport classification sauvegardé : {output_path}")

            results = report.as_dict()
            metrics_section = results["metrics"][0]["result"]["current"]
            performance = {"accuracy": metrics_section.get("accuracy"), "f1": metrics_section.get("f1")}

            self._update_model_performance_metrics(model_version, performance)
            return results

        except Exception as e:
            logger.error(f"Erreur génération classification Evidently : {e}")
            record_api_error("classification_report_generation")
            raise

    def generate_drift_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        output_path: Optional[Path] = None
    ) -> Dict:
        """Génère un rapport de data drift Evidently + met à jour les métriques."""
        try:
            logger.info("Génération du rapport Evidently : Data Drift...")
            report = Report(metrics=[DataDriftPreset()])
            report.run(reference_data=reference_data, current_data=current_data)

            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                report.save_html(str(output_path))
                logger.info(f"Rapport drift sauvegardé : {output_path}")

            results = report.as_dict()
            self._update_drift_metrics(results)
            return results

        except Exception as e:
            logger.error(f"Erreur génération drift Evidently : {e}")
            record_api_error("drift_report_generation")
            raise

    # -------------------------------------------------------------------------
    # ------------------------------ ORCHESTRATION ---------------------------
    # -------------------------------------------------------------------------
    def update_all_reports(self) -> str:
        """
        Charge les données de référence + logs courants,
        exécute les rapports Evidently,
        met à jour les métriques Prometheus.
        """
        settings = get_settings()
        logger.info("Mise à jour complète des rapports Evidently...")

        # --- Validation existence fichiers ---
        if not settings.REFERENCE_DATA_PATH.exists():
            return f"Fichier référence introuvable : {settings.REFERENCE_DATA_PATH}"

        if not settings.PREDICTION_LOG_PATH.exists():
            return f"Fichier prédictions introuvable : {settings.PREDICTION_LOG_PATH}"

        try:
            reference_df = pd.read_csv(settings.REFERENCE_DATA_PATH)
            current_df = pd.read_csv(settings.PREDICTION_LOG_PATH)
        except pandas.errors.EmptyDataError:
            return "Erreur : un des fichiers de données est vide."

        # --- Déterminer les colonnes de features ---
        if prediction_service.is_loaded():
            feature_cols = prediction_service.model.feature_names_in_.tolist()
        else:
            feature_cols = [col for col in reference_df.columns if col not in ("target", "prediction")]

        model_version = prediction_service.get_model_version()

        # ------------------------ DATA DRIFT REPORT ------------------------
        self.generate_drift_report(
            reference_data=reference_df[feature_cols],
            current_data=current_df[feature_cols],
            output_path=settings.REPORTS_DIR / "data_drift_report.html"
        )

        msg = "Rapport de dérive généré. "

        # ------------------------ CLASSIFICATION REPORT --------------------
        if not settings.GROUND_TRUTH_LOG_PATH.exists():
            logger.warning("Aucune vérité terrain → rapport performance ignoré.")
            return msg + "Pas de rapport performance (pas de vérité terrain)."

        ground_truth_df = pd.read_csv(settings.GROUND_TRUTH_LOG_PATH)
        if ground_truth_df.empty:
            return msg + "Pas de rapport performance (vérité terrain vide)."

        # Fusion sur l'identifiant unique
        merged = pd.merge(current_df, ground_truth_df, on="prediction_id", how="inner")
        if merged.empty:
            return msg + "Rapport performance ignoré (aucune correspondance)."

        if "target" not in reference_df.columns:
            return msg + "Impossible de générer le rapport classification (target manquante)."

        # Renommage propre
        merged = merged.rename(columns={"prediction_x": "prediction"})

        # Génération rapport performance
        self.generate_classification_report(
            reference_data=reference_df,
            current_data=merged,
            model_version=model_version,
            output_path=settings.REPORTS_DIR / "classification_report.html"
        )

        return msg + "Rapport de performance généré."


# Instance unique
evidently_service = EvidentlyService()
