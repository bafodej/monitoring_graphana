from pathlib import Path
from datetime import datetime
import pandas as pd
from loguru import logger

from app.services.logging_service import prediction_logger
from app.config import get_settings
from app.metrics import record_drift_metrics
from evidently.legacy.report import Report
from evidently.legacy.metrics import DataDriftTable


def main() -> None:
    """
    Exécute le monitoring Evidently (Data Drift) :
    - Vérifie la présence des fichiers de référence et des prédictions
    - Génère le rapport HTML de drift
    - Met à jour les métriques Prometheus
    """

    settings = get_settings()
    reference_path: Path = settings.REFERENCE_DATA_PATH
    prediction_log_path: Path = settings.PREDICTION_LOG_PATH
    reports_dir: Path = settings.REPORTS_DIR
    feature_cols = settings.FEATURE_COLUMNS

    # Créer le dossier des rapports si nécessaire
    reports_dir.mkdir(parents=True, exist_ok=True)

    logger.info(">>> Lancement du monitoring Evidently (Data Drift)...")

    # --- Vérification des fichiers ---
    if not reference_path.exists():
        logger.error(f"Fichier de référence introuvable : {reference_path}")
        return
    if not prediction_log_path.exists():
        logger.warning(f"Aucun fichier de prédictions trouvé : {prediction_log_path}")
        return

    try:
        # --- Charger les données ---
        reference_df = pd.read_csv(reference_path)
        current_df = prediction_logger.get_all_predictions()

        if current_df.empty:
            logger.warning("Aucune prédiction enregistrée → rien à analyser.")
            return

        # --- Vérifier que toutes les colonnes nécessaires existent ---
        missing_cols_ref = [col for col in feature_cols if col not in reference_df.columns]
        missing_cols_curr = [col for col in feature_cols if col not in current_df.columns]
        if missing_cols_ref or missing_cols_curr:
            logger.error(f"Colonnes manquantes dans le dataset : "
                         f"Référence={missing_cols_ref}, Prédictions={missing_cols_curr}")
            return

        # --- Créer et exécuter le rapport Data Drift ---
        report = Report(metrics=[DataDriftTable()])
        report.run(reference_data=reference_df[feature_cols], current_data=current_df[feature_cols])

        # --- Historisation du rapport HTML avec timestamp ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = reports_dir / f"data_drift_report_{timestamp}.html"
        report.save_html(str(output_file))
        logger.success(f"Rapport Data Drift généré : {output_file}")

        # --- Mettre à jour les métriques Prometheus dynamiquement ---
        record_drift_metrics(reference_path, prediction_log_path)

        # --- Log détaillé du drift ---
        drift_result = report.as_dict()['metrics'][0]['result']
        drift_score = drift_result.get('dataset_drift_score', 0.0)
        drifted_features = [f for f, v in drift_result['drift_by_columns'].items() if v['drift_detected']]

        logger.info(f"Score de drift global : {drift_score:.3f}")
        logger.info(f"Features driftées : {drifted_features if drifted_features else 'Aucune'}")

    except Exception as e:
        logger.exception(f"Erreur lors de la génération du rapport Data Drift : {e}")


if __name__ == "__main__":
    main()
