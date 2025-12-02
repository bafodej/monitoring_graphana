"""
Module de monitoring pour l'API de qualité de l'air.
Contient les métriques Prometheus personnalisées et la logique pour les rapports Evidently.
Inspiré par les meilleures pratiques de projets de monitoring ML.
"""
from prometheus_client import Gauge, Counter, Histogram, Summary
from loguru import logger
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset
from pathlib import Path
from typing import Dict, Optional


# ============================================================
# 🔥 1) MÉTRIQUES DE PERFORMANCE DE L'API (HTTP)
# ============================================================

http_requests_total = Counter(
    "http_requests_total",
    "Nombre total de requêtes HTTP reçues.",
    ["method", "handler", "status_code"]
)

http_requests_latency_seconds = Histogram(
    "http_requests_latency_seconds",
    "Latence des requêtes HTTP en secondes.",
    ["handler"],
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.5, 5.0, 10.0)
)

api_errors_total = Counter(
    "api_errors_total",
    "Nombre total d'erreurs inattendues de l'API.",
    ["error_type"]
)

# ============================================================
# 🔥 2) MÉTRIQUES DU MODÈLE DE MACHINE LEARNING
# ============================================================

ml_predictions_total = Counter(
    "ml_predictions_total",
    "Nombre total de prédictions ML effectuées.",
    ["model_version", "prediction_class"]
)

ml_prediction_latency_seconds = Histogram(
    "ml_prediction_latency_seconds",
    "Temps de latence pour les prédictions du modèle ML en secondes.",
    ["model_version"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
)

ml_prediction_confidence = Gauge(
    "ml_prediction_confidence",
    "Confiance de la dernière prédiction ML.",
    ["model_version", "prediction_class"]
)

ml_prediction_confidence_summary = Summary(
    'ml_prediction_confidence_summary',
    'Statistiques de confiance pour les prédictions (min, max, avg).',
    ['model_version']
)

# ============================================================
# 🔥 3) MÉTRIQUES DE SURVEILLANCE DU MODÈLE (MLOPS)
# ============================================================

ml_data_drift_score = Gauge(
    "ml_data_drift_score",
    "Score de dérive des données (0 = pas de dérive, 1 = dérive détectée)."
)

ml_feature_drift_detected = Counter(
    'ml_feature_drift_detected_total',
    'Compteur de détection de dérive par feature.',
    ['feature_name']
)

ml_model_accuracy = Gauge(
    "ml_model_accuracy",
    "Précision (accuracy) actuelle du modèle ML.",
    ["model_version"]
)

ml_model_f1 = Gauge(
    "ml_model_f1",
    "Score F1 actuel du modèle ML.",
    ["model_version"]
)

# ============================================================
# 🔥 4) MÉTRIQUES MÉTIER (CAPTEURS)
# ============================================================

air_temperature = Gauge("air_temperature_celsius", "Température de l'air en degrés Celsius.")
air_humidity = Gauge("air_humidity_percent", "Pourcentage d'humidité de l'air.")
air_co2 = Gauge("air_co2_ppm", "Concentration de CO2 en parties par million (ppm).")
air_pm25 = Gauge("air_pm25_micrograms_per_m3", "Concentration de PM2.5 en µg/m³.")
air_pm10 = Gauge("air_pm10_micrograms_per_m3", "Concentration de PM10 en µg/m³.")
air_tvoc = Gauge("air_tvoc_ppb", "Concentration de TVOC en parties par milliard (ppb).")
room_occupancy = Gauge("room_occupancy_status", "État d'occupation de la pièce (0 ou 1).")

# ============================================================
# 🔥 5) MÉTRIQUES SYSTÈME (VENTILATION)
# ============================================================

ventilation_status = Gauge(
    "ventilation_status",
    "État du système de ventilation (1 = activé, 0 = désactivé)."
)

ventilation_activations_total = Counter(
    "ventilation_activations_total",
    "Nombre total d'activations du système de ventilation."
)

# ============================================================
# 🔥 6) FONCTIONS UTILITAIRES POUR LES MÉTRIQUES
# ============================================================

def record_api_error(error_type: str):
    """Enregistre une erreur générique de l'API."""
    try:
        api_errors_total.labels(error_type=error_type).inc()
        logger.warning(f"Erreur API enregistrée : type={error_type}")
    except Exception as e:
        logger.error(f"Impossible d'enregistrer l'erreur API : {e}")

def record_prediction_metrics(model_version: str, prediction_class: str, confidence: float, latency: float):
    """Enregistre toutes les métriques pour une seule prédiction."""
    try:
        ml_predictions_total.labels(model_version=model_version, prediction_class=prediction_class).inc()
        ml_prediction_latency_seconds.labels(model_version=model_version).observe(latency)
        ml_prediction_confidence.labels(model_version=model_version, prediction_class=prediction_class).set(confidence)
        ml_prediction_confidence_summary.labels(model_version=model_version).observe(confidence)
        logger.info(f"Prédiction enregistrée: v={model_version}, classe={prediction_class}, confiance={confidence:.3f}, latence={latency:.4f}s")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des métriques de prédiction : {e}")
        record_api_error("prediction_metrics_recording")

def record_sensor_data(data: dict):
    """Enregistre les métriques des données des capteurs."""
    try:
        sensor_mapping = {
            "temperature": air_temperature,
            "humidity": air_humidity,
            "co2": air_co2,
            "pm25": air_pm25,
            "pm10": air_pm10,
            "tvoc": air_tvoc,
            "occupancy": room_occupancy,
        }
        for key, metric in sensor_mapping.items():
            if key in data and data[key] is not None:
                metric.set(data[key])
        logger.info("Données des capteurs enregistrées pour Prometheus.")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des données capteurs : {e}")
        record_api_error("sensor_data_recording")

def update_drift_metrics(drift_results: dict):
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

def update_model_performance_metrics(model_version: str, performance_results: dict):
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
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    model_version: str = "v1.0",
    output_path: Optional[Path] = None
) -> Dict:
    """Génère un rapport de performance de classification et met à jour les métriques."""
    try:
        logger.info("Génération du rapport de classification...")
        report = Report(metrics=[ClassificationPreset()])
        report.run(reference_data=reference_data, current_data=current_data, column_mapping=None)
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report.save_html(str(output_path))
            logger.info(f"Rapport de classification sauvegardé : {output_path}")
            
        results = report.as_dict()
        
        # Extraire les métriques et les mettre à jour
        class_metrics = results['metrics'][0]['result']['current']
        performance = {
            'accuracy': class_metrics.get('accuracy'),
            'f1': class_metrics.get('f1')
        }
        update_model_performance_metrics(model_version, performance)
        
        logger.info(f"Rapport de classification généré : Accuracy={performance['accuracy']:.3f}, F1={performance['f1']:.3f}")
        return results
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport de classification : {e}")
        record_api_error("classification_report_generation")
        raise

def generate_drift_report(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    output_path: Optional[Path] = None
) -> Dict:
    """Génère un rapport de détection de dérive et met à jour les métriques."""
    try:
        logger.info("Génération du rapport de dérive...")
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=reference_data, current_data=current_data)
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            report.save_html(str(output_path))
            logger.info(f"Rapport de dérive sauvegardé : {output_path}")
            
        results = report.as_dict()
        update_drift_metrics(results)
        
        logger.info("Rapport de dérive généré avec succès.")
        return results
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport de dérive : {e}")
        record_api_error("drift_report_generation")
        raise