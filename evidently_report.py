import pandas as pd
from evidently.legacy.report import Report
from evidently.legacy.metrics import DataDriftTable
from pathlib import Path
from loguru import logger

from app.config import get_settings

settings = get_settings()
reference_path = settings.REFERENCE_DATA_PATH
prediction_log_path = settings.PREDICTION_LOG_PATH
reports_dir = settings.REPORTS_DIR

# Vérifier l’existence des fichiers
if not reference_path.exists():
    logger.error(f"Fichier de référence introuvable : {reference_path}")
    raise FileNotFoundError(f"Fichier de référence introuvable : {reference_path}")

if not prediction_log_path.exists():
    logger.error(f"Fichier de prédictions introuvable : {prediction_log_path}")
    raise FileNotFoundError(f"Fichier de prédictions introuvable : {prediction_log_path}")

# S'assurer que le dossier reports existe
reports_dir.mkdir(parents=True, exist_ok=True)
report_path = reports_dir / "data_drift_report.html"

# Charger les données
reference_data = pd.read_csv(reference_path)
production_data = pd.read_csv(prediction_log_path)

feature_columns = ['temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy']
df_ref = reference_data[feature_columns]
df_prod = production_data[feature_columns]

# Créer et exécuter le rapport (legacy API)
report = Report(metrics=[DataDriftTable()])
report.run(reference_data=df_ref, current_data=df_prod)

# Sauvegarder le rapport
report.save_html(str(report_path))
logger.success(f"Rapport HTML de data drift généré : {report_path}")
