import pandas as pd
import logging
import argparse
from app.config import AppConfig

# Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

FULL_DATASET_PATH = AppConfig.MODEL_DIR / "IoT_Indoor_Air_Quality_Dataset.csv"
REFERENCE_DATA_PATH = AppConfig.REFERENCE_DATA_PATH
SAMPLE_SIZE = 500

def create_reference_data(force: bool = False):
    logging.info("--- Création du jeu de données de référence pour Evidently ---")

    # S'assurer que le dossier existe
    AppConfig.MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if REFERENCE_DATA_PATH.exists() and not force:
        logging.warning(f"Le fichier '{REFERENCE_DATA_PATH}' existe déjà. Utilisez --force pour le recréer.")
        return

    if not FULL_DATASET_PATH.exists():
        logging.error(f"Fichier source '{FULL_DATASET_PATH}' introuvable !")
        return

    try:
        df = pd.read_csv(FULL_DATASET_PATH)
        logging.info("Renommage des colonnes pour correspondre au modèle...")

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
            "Room_Occupancy_Count": "occupancy"
        }
        df = df.rename(columns=column_mapping)
        df['target'] = df['occupancy'].apply(lambda x: 0 if x > 0 else 1)

        n_sample = min(SAMPLE_SIZE, len(df))
        reference_df = df.sample(n=n_sample, random_state=42)
        reference_df.to_csv(REFERENCE_DATA_PATH, index=False)
        logging.info(f"Fichier de référence créé : '{REFERENCE_DATA_PATH}' ({n_sample} lignes)")
    except Exception as e:
        logging.error(f"Erreur lors de la création du fichier de référence : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prépare le jeu de données de référence.")
    parser.add_argument("--force", action="store_true", help="Récrée le fichier même s'il existe.")
    args = parser.parse_args()
    create_reference_data(force=args.force)
