# Utiliser une image Python 3.10 officielle
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY ./requirements.txt .

# Installer les dépendances
# --no-cache-dir pour ne pas stocker le cache et réduire la taille de l'image
# --upgrade pip pour s'assurer d'avoir la dernière version
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY ./app /app

# Exposer le port sur lequel l'API s'exécutera
EXPOSE 8000

# Commande pour lancer l'application avec Uvicorn
# --host 0.0.0.0 pour rendre l'API accessible de l'extérieur du conteneur
# --port 8000 pour correspondre au port exposé
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
