import pandas as pd
from evidently.legacy.report import Report
from evidently.legacy.metrics import DataDriftTable
from pathlib import Path

# Charger les données
reference_data = pd.read_csv("app/data/reference_data.csv")
production_data = pd.read_csv("data/predictions_log.csv")

feature_columns = ['temperature', 'humidity', 'co2', 'pm25', 'pm10', 'tvoc', 'occupancy']
df_ref = reference_data[feature_columns]
df_prod = production_data[feature_columns]

# Créer et exécuter le rapport (legacy API)
my_report = Report(metrics=[DataDriftTable()])
my_report.run(reference_data=df_ref, current_data=df_prod)

# Sauvegarder en HTML
my_report.save_html("reports/data_drift_report.html")

print(f"Rapport HTML généré : reports/data_drift_report.html")