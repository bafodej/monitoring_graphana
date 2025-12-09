# ============================
# 1️⃣ Build Stage
# ============================
FROM python:3.12-slim AS builder

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ============================
# 2️⃣ Final Stage
# ============================
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser
WORKDIR /home/appuser/code

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=appuser:appuser ./app /home/appuser/code/app
COPY --chown=appuser:appuser \
     ./prepare_reference_data.py \
     ./run_simulation.py \
     ./run_monitoring_analysis.py \
     /home/appuser/code/

# --- Créer le dossier des rapports ---
RUN mkdir -p /home/appuser/code/reports \
    && chown -R appuser:appuser /home/appuser/code/reports

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
