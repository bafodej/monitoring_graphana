# Monitoring d'une API de Machine Learning pour la Qualité de l'Air (IoT)

Ce projet met en œuvre un système complet pour le monitoring d'une application de Machine Learning. L'API, basée sur des données de capteurs IoT, prédit si un système de ventilation doit être activé pour maintenir une bonne qualité de l'air intérieur.

Le monitoring est assuré par une stack Prometheus, Grafana et Evidently AI, le tout orchestré avec Docker Compose.

## 🏛️ Architecture

Le système est composé de plusieurs services conteneurisés qui communiquent via un réseau Docker :

1.  **API (FastAPI)** : Le cœur de l'application. Elle sert le modèle de classification, expose un endpoint `/predict` et publie des métriques de performance (API et modèle) pour Prometheus.
2.  **Prometheus** : Un système de monitoring qui collecte (scrape) périodiquement les métriques exposées par l'API et cAdvisor.
3.  **Grafana** : Une plateforme de visualisation qui se connecte à Prometheus pour afficher les métriques sous forme de graphiques et de tableaux de bord.
4.  **cAdvisor** : Un agent qui collecte des métriques sur l'utilisation des ressources (CPU, RAM, réseau) de tous les conteneurs Docker.
5.  **Evidently AI** : Intégré à l'API, Evidently est utilisé pour générer des rapports sur la dérive des données (*data drift*) et la performance du modèle de classification.

## ✨ Fonctionnalités

-   **API de prédiction ML** : Endpoint pour prédire l'activation de la ventilation.
-   **Monitoring de performance API** : Suivi des requêtes HTTP, de la latence et des erreurs (via `prometheus-fastapi-instrumentator`).
-   **Monitoring du modèle ML** :
    -   Suivi de la performance (précision, F1-score).
    -   Détection de la dérive des données (*data drift*).
    -   Les métriques clés sont exposées pour Prometheus.
-   **Rapports Visuels** : Génération de rapports HTML détaillés avec Evidently AI.
-   **Visualisation centralisée** : Un tableau de bord Grafana pré-configuré pour visualiser l'ensemble des métriques.

## 🛠️ Technologies utilisées

-   **Backend** : FastAPI
-   **Monitoring** : Prometheus, Grafana, Evidently AI
-   **Conteneurisation** : Docker, Docker Compose
-   **Librairies Python** : Pandas, Scikit-learn (implicite), Loguru, Uvicorn

## 🚀 Démarrage rapide

### Prérequis

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation et Lancement

1.  **Clonez le dépôt :**
    ```bash
    git clone <URL_DU_DEPOT>
    cd <NOM_DU_DOSSIER>
    ```

2.  **Lancez les services avec Docker Compose :**
    Cette commande va construire l'image de l'API et démarrer tous les conteneurs en arrière-plan.
    ```bash
    docker-compose up -d --build
    ```

3.  **Vérifiez que les conteneurs sont bien en cours d'exécution :**
    ```bash
    docker-compose ps
    ```
    Vous devriez voir les services `api`, `prometheus`, `grafana` et `cadvisor` avec le statut `Up`.

## ⚙️ Comment utiliser le système

Une fois les services lancés, vous pouvez accéder aux différents composants :

### 1. API FastAPI

-   **URL de la documentation (Swagger)** : [http://localhost:8000/docs](http://localhost:8000/docs)
-   **Endpoint de santé** : [http://localhost:8000/health](http://localhost:8000/health)
-   **Endpoint des métriques Prometheus** : [http://localhost:8000/metrics](http://localhost:8000/metrics)

Vous pouvez utiliser la documentation interactive pour envoyer des requêtes de test à l'endpoint `/predict`.

### 2. Prometheus

-   **URL** : [http://localhost:9090](http://localhost:9090)
-   Pour vérifier que Prometheus collecte bien les métriques de l'API, allez dans `Status > Targets`. Vous devriez voir les cibles `fastapi-api` et `cadvisor` avec un état `UP`.

### 3. Grafana

-   **URL** : [http://localhost:3000](http://localhost:3000)
-   **Identifiants** :
    -   Utilisateur : `admin`
    -   Mot de passe : `admin` (défini dans `docker-compose.yml`)

Le tableau de bord "Air Quality Dashboard" devrait être automatiquement provisionné. Si ce n'est pas le cas, vous pouvez l'importer manuellement en utilisant le fichier JSON situé dans le dossier `grafana/`.

### 4. Rapports Evidently

Les rapports HTML sont générés et stockés dans le dossier `/reports` à la racine du projet. Vous pouvez les ouvrir directement avec votre navigateur pour analyser en détail la dérive des données ou la performance du modèle.

## 📂 Structure du projet

```
.
├── app/                  # Code source de l'application FastAPI
│   ├── routes/           # Fichiers de routes (endpoints)
│   ├── services/         # Logique métier (modèle, evidently)
│   ├── Dockerfile        # Instructions pour construire l'image de l'API
│   └── main.py           # Point d'entrée de l'application FastAPI
├── docker-compose.yml    # Fichier d'orchestration des services
├── grafana/              # Configuration et tableau de bord Grafana
├── prometheus/           # Fichier de configuration de Prometheus
├── reports/              # Rapports HTML générés par Evidently
└── README.md             # Cette documentation
```