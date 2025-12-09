"""
Module de monitoring pour l'API de qualité de l'air.
Définit les métriques Prometheus pour le monitoring de l'API, du modèle ML et des capteurs.
"""
from prometheus_client import Gauge, Counter, Histogram, Summary
from typing import Dict
from loguru import logger

# ============================================================
# 🔥 1) MÉTRIQUES DE PERFORMANCE DE L'API (HTTP)
# ============================================================

http_requests_latency_seconds = Histogram(
    "http_requests_latency_seconds",
    "Latence des requêtes HTTP en secondes.",
    ["handler"],
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.5, 5.0, 10.0),
)

api_errors_total = Counter(
    "api_errors_total",
    "Nombre total d'erreurs inattendues de l'API.",
    ["error_type"],
)

# ============================================================
# 🔥 2) MÉTRIQUES DU MODÈLE DE MACHINE LEARNING
# ============================================================

ml_predictions_total = Counter(
    "ml_predictions_total",
    "Nombre total de prédictions ML effectuées.",
    ["model_version", "prediction_class"],
)

ml_prediction_latency_seconds = Histogram(
    "ml_prediction_latency_seconds",
    "Temps de latence pour les prédictions ML (s).",
    ["model_version"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
)

ml_prediction_confidence = Gauge(
    "ml_prediction_confidence",
    "Confiance de la dernière prédiction ML.",
    ["model_version", "prediction_class"],
)

ml_prediction_confidence_summary = Summary(
    "ml_prediction_confidence_summary",
    "Statistiques de confiance pour les prédictions (min, max, avg).",
    ["model_version"],
)

# ============================================================
# 🔥 3) MÉTRIQUES DE SURVEILLANCE DU MODÈLE (MLOPS)
# ============================================================

ml_data_drift_score = Gauge(
    "ml_data_drift_score",
    "Score de dérive des données (0 = pas de dérive, 1 = dérive détectée).",
)

ml_feature_drift_detected = Counter(
    "ml_feature_drift_detected",
    "Compteur de détection de dérive par feature.",
    ["feature_name"],
)

ml_model_accuracy = Gauge(
    "ml_model_accuracy",
    "Précision (accuracy) actuelle du modèle ML.",
    ["model_version"],
)

ml_model_f1 = Gauge(
    "ml_model_f1",
    "Score F1 actuel du modèle ML.",
    ["model_version"],
)

# ============================================================
# 🔥 4) MÉTRIQUES MÉTIER (CAPTEURS)
# ============================================================

air_temperature = Gauge("air_temperature_celsius", "Température de l'air en degrés Celsius.")
air_humidity = Gauge("air_humidity_percent", "Pourcentage d'humidité de l'air.")
air_co2 = Gauge("air_co2_ppm", "Concentration de CO2 en ppm.")
air_pm25 = Gauge("air_pm25_micrograms_per_m3", "Concentration de PM2.5 en µg/m³.")
air_pm10 = Gauge("air_pm10_micrograms_per_m3", "Concentration de PM10 en µg/m³.")
air_tvoc = Gauge("air_tvoc_ppb", "Concentration de TVOC en ppb.")
room_occupancy = Gauge("room_occupancy_status", "État d'occupation de la pièce (0 ou 1).")

# ============================================================
# 🔥 5) MÉTRIQUES SYSTÈME (VENTILATION)
# ============================================================

ventilation_status = Gauge(
    "ventilation_status",
    "État du système de ventilation (1 = activé, 0 = désactivé).",
)

ventilation_activations_total = Counter(
    "ventilation_activations_total",
    "Nombre total d'activations du système de ventilation.",
)

# ============================================================
# 🔥 6) FONCTIONS UTILITAIRES POUR LES MÉTRIQUES
# ============================================================

def record_api_error(error_type: str) -> None:
    """Enregistre une erreur générique de l'API."""
    try:
        api_errors_total.labels(error_type=error_type).inc()
        logger.warning(f"Erreur API enregistrée | type={error_type}")
    except Exception as e:
        logger.error(f"Impossible d'enregistrer l'erreur API : {e}")


def record_prediction_metrics(model_version: str, prediction_class: str, confidence: float, latency: float) -> None:
    """Enregistre toutes les métriques pour une prédiction ML."""
    try:
        ml_predictions_total.labels(model_version=model_version, prediction_class=prediction_class).inc()
        ml_prediction_latency_seconds.labels(model_version=model_version).observe(latency)
        ml_prediction_confidence.labels(model_version=model_version, prediction_class=prediction_class).set(confidence)
        ml_prediction_confidence_summary.labels(model_version=model_version).observe(confidence)
        logger.info(f"Prédiction enregistrée | v={model_version}, classe={prediction_class}, "
                    f"confiance={confidence:.3f}, latence={latency:.4f}s")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des métriques de prédiction : {e}")
        record_api_error("prediction_metrics_recording")


def record_sensor_data(data: dict[str, float]) -> None:
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
