# Monitoring de Modèle de Machine Learning avec Prometheus, Grafana & Evidently AI

Ce projet est une démonstration complète d'une stack MLOps pour le monitoring d'un modèle de Machine Learning en production. Il intègre une API FastAPI, une base de données de séries temporelles (Prometheus), un outil de visualisation (Grafana) et une bibliothèque de validation de données et de modèles (Evidently AI).

## 🎯 Objectif

L'objectif est de déployer un modèle de classification de la qualité de l'air et de monitorer :
1.  **Les métriques système et API** : performance des conteneurs (CPU, RAM), latence des requêtes, taux d'erreur.
2.  **Les métriques métier** : distribution des prédictions, nombre d'activations du système de ventilation.
3.  **Les métriques de performance du modèle** : dérive des données (data drift), dérive du concept (concept drift), et précision du modèle au fil du temps.

## ✨ Fonctionnalités

-   **API FastAPI** : Sert un modèle `scikit-learn` pour prédire la nécessité d'activer un système de ventilation.
-   **Prometheus & cAdvisor** : Collecte des métriques sur l'API et les conteneurs Docker.
-   **Grafana** : Fournit des dashboards pré-configurés pour visualiser toutes les métriques en temps réel.
-   **Evidently AI** : Génère des rapports HTML pour analyser la dérive des données et la performance du modèle.
-   **Docker Compose** : Orchestre l'ensemble des services pour un déploiement simple et reproductible.
-   **Simulation** : Inclut des scripts pour simuler du trafic et générer des données de production et de vérité terrain.

## 🏗️ Architecture

Le projet est composé des services Docker suivants :

-   `api` (`airquality-ml-api`) : L'application FastAPI qui expose le modèle via un endpoint `/predict`. Elle expose également un endpoint `/metrics` pour Prometheus.
-   `prometheus` : Configure pour scraper les métriques de `api` et `cadvisor`.
-   `grafana` : Se connecte à Prometheus comme source de données et provisionne automatiquement deux dashboards.
-   `cadvisor` : Expose les métriques de performance (CPU, RAM, réseau) de tous les conteneurs en cours d'exécution.
-   `prepare_data_task` : Une tâche ponctuelle qui prépare un jeu de données de référence pour Evidently.
-   `run_simulation_task` : Une tâche ponctuelle qui envoie des requêtes de prédiction à l'API et soumet des feedbacks (vérité terrain).
-   `generate_report_task` : Une tâche ponctuelle qui s'exécute après la simulation pour générer les rapports de monitoring du modèle avec Evidently.

## 🚀 Démarrage Rapide

### Prérequis
*   Docker
*   Docker Compose

## Installation et Lancement

1.  **Clonez le dépôt :**
    ```bash
    git clone <url-du-repo>
    cd <nom-du-repo>
    ```

2.  **Lancez l'ensemble de la stack :**
    Exécutez la commande suivante à la racine du projet.
    ```bash
    docker compose up -d --build
    ```
    Cette commande va :
    -   Construire l'image Docker pour l'application FastAPI.
    -   Démarrer tous les services en arrière-plan (`-d`).
    -   Exécuter les tâches de préparation des données, de simulation et de génération de rapport dans le bon ordre grâce aux `depends_on`.

## 🌐 Accès aux Services

Une fois les conteneurs démarrés, les services sont accessibles aux adresses suivantes :

-   **API (Swagger UI)** : http://localhost:8000/docs
-   **Prometheus** : http://localhost:9090
-   **Grafana** : http://localhost:3000
    -   **Login** : `admin`
    -   **Mot de passe** : `admin`
-   **cAdvisor** : http://localhost:8080

## 📊 Monitoring et Rapports

### Dashboards Grafana

Connectez-vous à Grafana. Deux dashboards sont automatiquement provisionnés :

1.  **API & System Monitoring** : Affiche les métriques de performance de l'API (latence, taux de requêtes, erreurs) et l'utilisation des ressources des conteneurs (CPU, mémoire).
2.  **ML Model Monitoring** : Affiche les métriques spécifiques au modèle de Machine Learning (score de dérive des données, distribution des prédictions, performance du modèle, etc.).

### Rapports Evidently AI

Après l'exécution de la simulation, les rapports d'analyse sont disponibles dans le dossier `./reports/` à la racine du projet :

-   `data_drift_report.html` : Analyse la dérive entre les données de référence et les données de production.
-   `classification_report.html` : Analyse la performance du modèle de classification (précision, F1-score, matrice de confusion) en se basant sur la vérité terrain soumise.

Ouvrez ces fichiers dans votre navigateur pour explorer les analyses.

## 🧹 Arrêter les services

Pour arrêter tous les conteneurs, exécutez :

```bash
docker compose down
```

Pour nettoyer également les volumes (attention, cela supprime les données de Prometheus et Grafana) :

```bash
docker compose down -v
```

## 🔮 Pistes d'amélioration

-   **Alerting** : Mettre en place Alertmanager pour envoyer des notifications (ex: sur Slack) lorsque le data drift dépasse un certain seuil.
-   **Pipeline de CI/CD** : Automatiser les tests et le déploiement avec des outils comme GitHub Actions.
-   **Registre de modèles** : Utiliser un outil comme MLflow pour versionner et gérer les modèles de manière plus structurée.
-   **Retraining** : Déclencher un pipeline de ré-entraînement automatique lorsque les performances du modèle se dégradent.