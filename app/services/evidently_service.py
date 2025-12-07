from pathlib import Path
from typing import Dict, Optional
import logging
import pandas.errors

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset

from ..metrics import (
    ml_data_drift_score,
    ml_feature_drift_detected,
    ml_model_accuracy,
    ml_model_f1,
    record_api_error
)
from .prediction_services import prediction_service
from ..config import AppConfig

logger = logging.getLogger(__name__)

class EvidentlyService:
    """
    Service pour gérer la génération de rapports et les métriques avec Evidently AI.
    """

    def _update_drift_metrics(self, drift_results: dict):
        """Met à jour les métriques Prometheus avec les résultats de dérive d'Evidently."""
        try:
            metrics = drift_results.get('metrics', [])
            for metric in metrics:
                if metric.get('metric') == 'DatasetDriftMetric':
                    result = metric.get('result', {})
                    drift_score = result.get('dataset_drift_score', 0)
                    ml_data_drift_score.set(drift_score)

                    drift_by_columns = result.get('drift_by_columns', {})
                    for feature_name, feature_drift in drift_by_columns.items():
                        if feature_drift.get('drift_detected', False):
                            ml_feature_drift_detected.labels(feature_name=feature_name).inc()
                    
                    logger.info(f"Métriques de dérive mises à jour : score={drift_score:.3f}")
                    break
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques de dérive : {e}")
            record_api_error("drift_metrics_update")

    def _update_model_performance_metrics(self, model_version: str, performance_results: dict):
        """Met à jour l'accuracy et le F1-score du modèle."""
        try:
            accuracy = performance_results.get('accuracy')
            f1 = performance_results.get('f1')
            
            if accuracy is not None:
                ml_model_accuracy.labels(model_version=model_version).set(accuracy)
                logger.info(f"Accuracy du modèle (v={model_version}) mise à jour : {accuracy:.3f}")
            
            if f1 is not None:
                ml_model_f1.labels(model_version=model_version).set(f1)
                logger.info(f"F1-score du modèle (v={model_version}) mis à jour : {f1:.3f}")

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques de performance : {e}")
            record_api_error("performance_metrics_update")

    def generate_classification_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        model_version: str = "v1.0",
        output_path: Optional[Path] = None
    ) -> Dict:
        """Génère le rapport de performance de classification."""
        try:
            logger.info("Génération du rapport de classification...")
            report = Report(metrics=[ClassificationPreset()])
            report.run(reference_data=reference_data, current_data=current_data)

            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                report.save_html(str(output_path))
                logger.info(f"Rapport de classification sauvegardé : {output_path}")
                
            results = report.as_dict()
            
            class_metrics = results['metrics'][0]['result']['current']
            performance = {'accuracy': class_metrics.get('accuracy'), 'f1': class_metrics.get('f1')}
            self._update_model_performance_metrics(model_version, performance)
            
            logger.info(f"Rapport de classification généré : Accuracy={performance['accuracy']:.3f}, F1={performance['f1']:.3f}")
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport de classification : {e}")
            record_api_error("classification_report_generation")
            raise

    def generate_drift_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        output_path: Optional[Path] = None
    ) -> Dict:
        """Génère le rapport de dérive des données."""
        try:
            logger.info("Génération du rapport de dérive...")
            report = Report(metrics=[DataDriftPreset()])
            report.run(reference_data=reference_data, current_data=current_data)
            
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                report.save_html(str(output_path))
                logger.info(f"Rapport de dérive sauvegardé : {output_path}")
                
            results = report.as_dict()
            self._update_drift_metrics(results)
            
            logger.info("Rapport de dérive généré avec succès.")
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport de dérive : {e}")
            record_api_error("drift_report_generation")
            raise

    def update_all_reports(self) -> str:
        """
        Orchestre la génération de tous les rapports Evidently (dérive, performance)
        en chargeant les données nécessaires.
        """
        logger.info("Début de la mise à jour des rapports Evidently...")

        # --- Vérification et chargement des données ---
        if not AppConfig.REFERENCE_DATA_PATH.exists():
            msg = f"Fichier de données de référence introuvable: {AppConfig.REFERENCE_DATA_PATH}"
            logger.error(msg)
            return msg
        if not AppConfig.PREDICTION_LOG_PATH.exists():
            msg = f"Fichier de log de prédictions introuvable: {AppConfig.PREDICTION_LOG_PATH}"
            logger.error(msg)
            return msg

        try:
            reference_df = pd.read_csv(AppConfig.REFERENCE_DATA_PATH)
            current_predictions_df = pd.read_csv(AppConfig.PREDICTION_LOG_PATH)
        except pandas.errors.EmptyDataError as e:
            msg = f"Un des fichiers de données est vide : {e}"
            logger.error(msg)
            return msg
        
        # Utiliser les features du modèle chargé pour plus de flexibilité
        feature_cols = prediction_service.model.feature_names_in_.tolist() if prediction_service.is_loaded() else reference_df.columns.drop(['target', 'prediction'], errors='ignore').tolist()
        model_version = prediction_service.get_model_version()

        # --- Génération du Rapport de Dérive des Données ---
        self.generate_drift_report(
            reference_data=reference_df[feature_cols].copy(),
            current_data=current_predictions_df[feature_cols],
            output_path=AppConfig.REPORTS_DIR / "data_drift_report.html"
        )
        logger.info("Rapport de dérive des données généré.")
        report_message = "Rapport de dérive généré. "

        # --- Génération du Rapport de Performance ---
        if not AppConfig.GROUND_TRUTH_LOG_PATH.exists() or pd.read_csv(AppConfig.GROUND_TRUTH_LOG_PATH).empty:
            logger.warning("Fichier de vérité terrain introuvable ou vide. Le rapport de performance est ignoré.")
            report_message += "Rapport de performance ignoré (pas de vérité terrain)."
        else:
            ground_truth_df = pd.read_csv(AppConfig.GROUND_TRUTH_LOG_PATH)
            merged_df = pd.merge(current_predictions_df, ground_truth_df, on="prediction_id")

            if merged_df.empty:
                logger.warning("Aucune prédiction ne correspond à la vérité terrain. Le rapport de performance est ignoré.")
                report_message += "Rapport de performance ignoré (aucune correspondance de vérité terrain)."
            else:
                # Evidently peut gérer l'absence de 'prediction' dans les données de référence
                # Il suffit de s'assurer que les colonnes de features et la 'target' sont présentes.
                if 'target' not in reference_df.columns:
                    logger.error("La colonne 'target' est manquante dans les données de référence. Impossible de générer le rapport de classification.")
                    return "Erreur: 'target' manquante dans les données de référence."

                self.generate_classification_report(
                    reference_data=reference_df,
                    current_data=merged_df.rename(columns={'prediction_x': 'prediction'}), # S'assurer que la colonne de prédiction est bien nommée
                    model_version=model_version,
                    output_path=AppConfig.REPORTS_DIR / "classification_report.html"
                )
                logger.info("Rapport de performance de classification généré avec la vérité terrain.")
                report_message += "Rapport de performance généré."

        logger.info("Mise à jour des rapports Evidently terminée.")
        return report_message


# Instance unique du service pour être utilisée dans l'application
evidently_service = EvidentlyService()
