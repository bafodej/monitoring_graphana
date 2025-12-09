# GEMINI.md

## 🎯 Objectif du projet
Ce projet est une API FastAPI pour la prédiction de la qualité de l’air intérieur et la gestion automatique de la ventilation.
L’API utilise un modèle RandomForest pré-entraîné (`indoor_aqi_model.pkl`) pour décider si la ventilation doit être activée ou désactivée.
Le projet inclut également la collecte de feedback utilisateur (vérité terrain) et le suivi de dérive et de performance via Evidently AI.

## 🗂 Structure du projet

```
app/
 ├─ config.py             # Configuration centralisée des chemins
 ├─ routes/
 │   ├─ prediction_route.py
 │   └─ feedback_route.py
 ├─ services/
 │   ├─ prediction_services.py
 │   └─ evidently_service.py
 ├─ shemas/
 │   └─ prediction_shemas.py
 └─ data/
     ├─ indoor_aqi_model.pkl
     └─ IoT_Indoor_Air_Quality_Dataset.csv
reports/
 └─ *.csv / *.html (logs et rapports)
scripts/
 ├─ run_simulation.py
 └─ run_monitoring_analysis.py
```

## 🧩 Fonctionnalités principales

### 1. Prédiction de qualité de l’air
- Endpoint : `POST /predict`
- Entrée : capteurs  
```json
{
  "temperature": 28.0,
  "humidity": 70.0,
  "co2": 1800,
  "pm25": 80.0,
  "pm10": 120.0,
  "tvoc": 400,
  "occupancy": 50
}
```
- Sortie :  
```json
{
  "prediction_id": "<uuid>",
  "prediction": 0 | 1,
  "confidence": 0.85
}
```
- Convention :  
  - `1` → Good → ventilation désactivée  
  - `0` → Moderate / Poor → ventilation activée

### 2. Feedback / vérité terrain
- Endpoint : `POST /feedback`
- Permet de soumettre le résultat réel pour une prédiction.
- Stocké dans `reports/ground_truth.csv`

### 3. Monitoring et métriques
- Suivi Prometheus :
  - Latence, confiance, nombre d’activations de ventilation
  - Dérive des features
  - Performance du modèle (accuracy, F1)
- Rapports Evidently : dérive (`DataDriftPreset`) et performance (`ClassificationPreset`)

## 🛠 Directives pour Gemini AI

1. **Modèle ML**
   - Toujours utiliser `indoor_aqi_model.pkl`.
   - La prédiction binaire se fait ainsi :  
     ```python
     binary_prediction = 1 if model.classes_[label_index] == "Good" else 0
     ```
   - Ne jamais changer le mapping 0/1.

2. **Endpoints**
   - Conserver `/predict` et `/feedback`.
   - Retourner toujours un JSON conforme à `PredictionOutput` ou `FeedbackInput`.

3. **Feature engineering**
   - Colonnes utilisées pour la prédiction :  
     `["temperature", "humidity", "co2", "pm25", "pm10", "tvoc", "occupancy"]`
   - La transformation des colonnes doit être cohérente avec le notebook original.

4. **Logs**
   - Utiliser `loguru` ou `logging` pour les actions critiques.
   - Logger toutes les erreurs avec détails.

5. **Docker & chemins**
   - Respecter `AppConfig` pour tous les chemins.
   - Compatible avec Docker (`/home/appuser/code`).

6. **Tests et simulations**
   - `run_simulation.py` : tests de l’API + feedback.
   - `run_monitoring_analysis.py` : tests des rapports Evidently.

7. **Conventions**
   - Les prédictions et feedbacks doivent rester compatibles avec Evidently.
   - Ne jamais renommer les endpoints existants.
   - Toujours commenter les étapes critiques.

## 💡 Bonnes pratiques pour Gemini AI

- Vérifier les colonnes et la cohérence des données avant d’écrire du code.
- Respecter le mapping binaire `0/1`.
- Toujours utiliser les fichiers `.pkl` et `.csv` existants pour prédictions et monitoring.
- Signaler toute modification des features ou du modèle.
- Écrire des commentaires explicatifs pour ML et API.
- Les changements structurels doivent être validés pour compatibilité avec Evidently et Prometheus.

