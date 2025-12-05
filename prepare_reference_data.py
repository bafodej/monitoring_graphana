import pandas as pd
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

# Définition des chemins
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "app" / "data"
FULL_DATASET_PATH = DATA_DIR / "IoT_Indoor_Air_Quality_Dataset.csv"
REFERENCE_DATA_PATH = DATA_DIR / "reference_data.csv"

# Nombre d'échantillons à prendre pour le jeu de données de référence
SAMPLE_SIZE = 500

def create_reference_data():
    """
    Crée le fichier reference_data.csv en prenant un échantillon
    du jeu de données complet et en renommant les colonnes.
    """
    logging.info("--- Création du jeu de données de référence pour Evidently ---")

    # Vérifier si le fichier source existe
    if not FULL_DATASET_PATH.exists():
        logging.error(f"Le fichier source '{FULL_DATASET_PATH}' est introuvable. Impossible de créer le fichier de référence.")
        return

    # Vérifier si le fichier de référence existe déjà
    if REFERENCE_DATA_PATH.exists():
        logging.warning(f"Le fichier de référence '{REFERENCE_DATA_PATH}' existe déjà. Pour le recréer, supprimez-le manuellement et relancez le script.")
        return

    try:
        # Charger le jeu de données complet
        logging.info(f"Chargement du jeu de données complet depuis '{FULL_DATASET_PATH}'...")
        df = pd.read_csv(FULL_DATASET_PATH)
        
        # --- NOUVELLE ÉTAPE : RENOMMAGE DES COLONNES ---
        logging.info("Renommage des colonnes pour correspondre au modèle...")
        column_mapping = {
            "Temperature (?C)": "temperature",
            "Humidity (%)": "humidity",
            "CO2 (ppm)": "co2",
            "PM2.5 (?g/m?)": "pm25",
            "PM10 (?g/m?)": "pm10",
            "TVOC (ppb)": "tvoc",
            "Occupancy Count": "occupancy"
        }
        df = df.rename(columns=column_mapping)
        # ------------------------------------------------

        # Prendre un échantillon aléatoire
        logging.info(f"Prélèvement d'un échantillon aléatoire de {SAMPLE_SIZE} lignes...")
        if len(df) < SAMPLE_SIZE:
            logging.warning(f"Le jeu de données complet est plus petit que la taille de l'échantillon ({len(df)} < {SAMPLE_SIZE}). Utilisation de toutes les données.")
            reference_df = df
        else:
            reference_df = df.sample(n=SAMPLE_SIZE, random_state=42)

        # Sauvegarder l'échantillon
        reference_df.to_csv(REFERENCE_DATA_PATH, index=False)
        logging.info(f"Succès ! Fichier de référence créé avec les bonnes colonnes : '{REFERENCE_DATA_PATH}'")

    except Exception as e:
        logging.error(f"Une erreur est survenue lors de la création du fichier de référence: {e}")

if __name__ == "__main__":
    create_reference_data()