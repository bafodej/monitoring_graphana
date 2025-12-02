"""
Ce service est un wrapper autour des fonctions de reporting d'Evidently
définies dans app.metrics.
"""
from app.metrics import generate_classification_report, generate_drift_report

# Pourrait être utilisé pour instancier un objet "service" si nécessaire,
# mais pour l'instant, nous exposons simplement les fonctions.
__all__ = ["generate_classification_report", "generate_drift_report"]