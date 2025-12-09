from pathlib import Path
import pandas as pd
import sys
from loguru import logger
import argparse

from app.config import get_settings

SAMPLE_SIZE = 500


def create_reference_data(force: bool = False) -> None:
    """
    Crée le fichier de données de référence pour Evidently.
    Si le fichier existe et `force=False`, la fonction ne fait rien.
    """
    settings = get_settings()
    full_dataset_path: Path = settings.MODEL_DIR / "IoT_Indoor_Air_Quality_Dataset.csv"
    reference_data_path: Path = settings.REFERENCE_DATA_PATH

    logger.info("=== Création du jeu de données de référence pour Evidently ===")

    # S'assurer que le dossier existe
    settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if reference_data_path.exists() and not force:
        logger.warning(
            f"Le fichier '{reference_data_path}' existe déjà. Utilisez --force pour le recréer."
        )
        return

    if not full_dataset_path.exists():
        logger.error(f"Fichier source introuvable : '{full_dataset_path}'")
        sys.exit(1)

    try:
        df = pd.read_csv(full_dataset_path)
        logger.info("Renommage des colonnes pour correspondre au modèle...")

        column_mapping = {
            "Temperature[C]": "temperature",
            "Humidity[%]": "humidity",
            "TVOC[ppb]": "tvoc",
            "eCO2[ppm]": "co2",
            "Raw H2": "raw_h2",
            "Raw Ethanol": "raw_ethanol",
            "Pressure[hPa]": "pressure",
            "PM1.0": "pm10",
            "PM2.5": "pm25",
            "NC0.5": "nc05",
            "NC1.0": "nc10",
            "NC2.5": "nc25",
            "CNT": "cnt",
            "Fire Alarm": "fire_alarm",
            "Room_Occupancy_Count": "occupancy",
        }

        df = df.rename(columns=column_mapping)
        df["target"] = df["occupancy"].apply(lambda x: 0 if x > 0 else 1)

        n_sample = min(SAMPLE_SIZE, len(df))
        reference_df = df.sample(n=n_sample, random_state=42)

        reference_data_path.parent.mkdir(parents=True, exist_ok=True)
        reference_df.to_csv(reference_data_path, index=False)
        logger.success(f"Fichier de référence créé : '{reference_data_path}' ({n_sample} lignes)")

    except Exception as e:
        logger.error(f"Erreur lors de la création du fichier de référence : {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prépare le jeu de données de référence pour Evidently.")
    parser.add_argument("--force", action="store_true", help="Récrée le fichier même s'il existe.")
    args = parser.parse_args()
    create_reference_data(force=args.force)
