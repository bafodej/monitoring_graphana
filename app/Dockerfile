# --- Étape 1 : Builder ---
FROM python:3.10-slim AS builder

WORKDIR /code

# Installer gcc et outils nécessaires pour compiler certaines dépendances
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et créer l'environnement virtuel
COPY requirements.txt requirements.txt
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Étape 2 : Image finale ---
FROM python:3.10-slim

# Installer curl pour healthchecks et utilitaires
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd --create-home appuser
WORKDIR /home/appuser/code

# Copier l'environnement Python depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Copier l'application et les scripts
COPY --chown=appuser:appuser ./app /home/appuser/code/app
COPY --chown=appuser:appuser ./prepare_reference_data.py \
                             ./run_simulation.py \
                             ./run_monitoring_analysis.py \
                             /home/appuser/code/

# Harmoniser PATH
ENV PATH="/opt/venv/bin:$PATH"
USER appuser

# Exposer le port FastAPI
EXPOSE 8000

# Commande par défaut : lancer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
