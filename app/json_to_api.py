#!/usr/bin/env python3
"""
Script : json_to_api.py
Objectif :
  - Lire un fichier JSON contenant une liste d'objets
  - OU générer un flux de données simulées (--simulate)
  - Envoyer les données vers une API en boucle continue
  - Gestion retry + logs
"""

import json
import argparse
import logging
import time
import requests
import random
from typing import Any, Dict, List


# ----------------------------------
# CONFIG LOGGING
# ----------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ----------------------------------
# FONCTIONS
# ----------------------------------
def load_json(path: str) -> List[Dict[str, Any]]:
    """Charge un fichier JSON contenant une liste d'objets."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            logger.info("Objet unique détecté → conversion en liste.")
            data = [data]

        if not isinstance(data, list):
            raise ValueError("Le JSON doit contenir une LISTE d'objets.")

        logger.info(f"JSON chargé : {len(data)} éléments trouvés.")
        return data

    except Exception as e:
        logger.error(f"Erreur de chargement du JSON : {e}")
        raise


def generate_simulated_entry() -> Dict[str, Any]:
    """Génère une mesure simulée réaliste."""

    return {
        "temperature": round(random.uniform(18, 32), 1),
        "humidity": round(random.uniform(30, 80), 1),
        "co2": random.randint(300, 2000),
        "pm25": round(random.uniform(5, 80), 1),
        "pm10": round(random.uniform(10, 150), 1),
        "tvoc": random.randint(10, 500),
        "occupancy": random.randint(0, 60),
    }


def post_with_retry(url: str, payload: Dict[str, Any], retries: int = 3, delay: int = 2) -> bool:
    """Envoie une requête POST avec retry."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code in (200, 201):
                logger.info(f"POST OK ({response.status_code}) : {payload}")
                return True
            else:
                logger.warning(
                    f"POST échoué ({response.status_code}). Tentative {attempt}/{retries}."
                )
        except Exception as e:
            logger.error(f"Erreur réseau : {e}. Tentative {attempt}/{retries}.")
        time.sleep(delay)
    return False


# ----------------------------------
# MAIN
# ----------------------------------
def main():
    parser = argparse.ArgumentParser(description="Envoi JSON -> API en boucle")
    parser.add_argument("--file", help="Chemin du fichier JSON")
    parser.add_argument("--endpoint", required=True, help="URL de l'API destination")
    parser.add_argument("--interval", type=float, default=2.0, help="Intervalle entre envois (sec)")
    parser.add_argument("--simulate", action="store_true", help="Activer la génération aléatoire")

    args = parser.parse_args()

    # Charge JSON si on n'est pas en mode simulation
    data_list = []
    if not args.simulate:
        if not args.file:
            raise ValueError("Vous devez fournir --file ou activer --simulate.")
        data_list = load_json(args.file)

    logger.info(f"Envoi vers endpoint : {args.endpoint}")
    logger.info("Mode simulation activé" if args.simulate else "Mode JSON fichier")

    index = 0

    try:
        while True:
            if args.simulate:
                entry = generate_simulated_entry()
            else:
                entry = data_list[index]
                index = (index + 1) % len(data_list)

            post_with_retry(args.endpoint, entry)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur. Fin du script.")


if __name__ == "__main__":
    main()
