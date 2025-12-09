# COPILOT.md — Règles et instructions pour GitHub Copilot

## 📌 Objectif du projet
Ce projet contient :
- une API FastAPI
- un modèle Machine Learning sérialisé en `.pkl`
- un système de monitoring + simulation
- un Docker Compose multi-service
- des logs + rapports exposés dans `/reports`

L'objectif principal :
👉 Faire des prédictions AQI et retourner **0 (poor/moderate)** ou **1 (good)**.

---

# 📁 Architecture du projet

```
app/
  ├── main.py               # FastAPI app
  ├── api/                  # Endpoints
  ├── core/                 # Logique interne
  ├── services/             # Modules métiers
  ├── config.py             # Chemins centralisés
  └── data/
      ├── indoor_aqi_model.pkl
      ├── version.txt
      ├── reference_data.csv

docker/
  ├── Dockerfile.api
  ├── Dockerfile.simulation
  ├── Dockerfile.monitoring

reports/
  ├── prediction_data.csv
  ├── ground_truth.csv
  └── metrics_cache.json
```

---

# ⚙️ Règles pour le modèle ML

## Charger le modèle
Toujours charger le modèle depuis :

```python
from app.config import AppConfig
model = joblib.load(AppConfig.MODEL_PATH)
```

## Données d'entrée (features)
Les features **doivent strictement être** :

```python
[
    "temperature",
    "humidity",
    "co2",
    "pm25",
    "pm10",
    "tvoc",
    "occupancy"
]
```

⚠️ Ne jamais renommer / réordonner ces colonnes.

## Valeur cible (target)
Le modèle retourne :

- `0` = poor/moderate
- `1` = good

Copilot doit **toujours respecter cette convention** et éviter toute classification texte.

---

# 🔌 Règles FastAPI

## Endpoints
Toujours :

- utiliser des modèles Pydantic pour les entrées/sorties
- typer les fonctions
- retourner un JSON structuré comme :

```json
{
  "status": "success",
  "prediction": 1,
  "model_version": "1.0.0"
}
```

## Exemple de prédiction
```python
@app.post("/predict")
def predict(data: SensorInput):
    pred = model.predict([data.to_list()])[0]
    return {"prediction": int(pred)}
```

Copilot doit respecter ce format.

---

# 🐳 Règles Docker

## Docker Compose
Les services sont :

```
api
simulator
monitoring
```

Copilot doit :

- toujours utiliser `Dockerfile.api` pour l'API
- toujours utiliser `Dockerfile.simulation` pour la simulation
- toujours utiliser `Dockerfile.monitoring` pour le monitoring
- ne jamais ajouter de services inutiles

## Volume partagé obligatoire
```
reports:/home/appuser/code/reports
```

Copilot doit s'assurer que chaque service lit/écrit dans ce même volume.

---

# 🧪 Tests & Monitoring

- Les scripts de simulation écrivent dans `prediction_data.csv`
- Le monitoring lit les logs, calcule les métriques, les cache dans `metrics_cache.json`
- Toute nouvelle fonctionnalité doit respecter ces fichiers existants

---

# 📑 Style & Qualité

## Python
- respecter PEP8
- préférer `pathlib.Path`
- utiliser `logging`, jamais `print`
- typer toutes les fonctions
- utiliser des dataclasses si approprié

## FastAPI
- toujours utiliser `@router.post`, `@router.get`
- séparer les endpoints dans `app/api/`

## Docker
- ne jamais installer numpy/pandas hors du bon service
- API = minimal + uniquement librairies nécessaires au modèle
- Simulation = numpy random
- Monitoring = pandas + scikit-learn

---

# 🚀 Quand Copilot doit refuser
Copilot ne doit pas :
- créer de nouveaux modèles ML
- changer la structure des features
- modifier la valeur 0/1
- créer des fichiers en doublon
- modifier les chemins dans `AppConfig`

---

# 📘 Aide à la génération de code

Si Copilot génère du code pour :
- **un endpoint** → proposer automatiquement un modèle Pydantic
- **un script ML** → charger le `.pkl` existant, ne jamais ré-entraîner
- **du logging** → utiliser `logging.getLogger(__name__)`
- **un Dockerfile** → baser sur `python:3.11-slim`

---

# ✔️ Fin du fichier
Copilot doit respecter toutes les règles ci-dessus pour toute génération dans ce projet.

