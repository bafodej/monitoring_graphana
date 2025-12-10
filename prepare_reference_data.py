from pathlib import Path
import pandas as pd
import sys
from loguru import logger
import argparse

from app.config import get_settings

def create_reference_data(force: bool = False) -> None:
    """
    Crée le fichier de données de référence pour Evidently.
    - Lecture du dataset original
    - Renommage des colonnes
    - Sélection uniquement des colonnes utiles
    - Création d'une colonne target : 0 si occupancy > 0 sinon 1
    - Échantillonnage propre
    """
    settings = get_settings()
    full_dataset_path: Path = settings.MODEL_DIR / "IoT_Indoor_Air_Quality_Dataset.csv"
    reference_data_path: Path = settings.REFERENCE_DATA_PATH

    logger.info("=== Création du jeu de données de référence Evidently ===")

    # Vérification existence
    if reference_data_path.exists() and not force:
        logger.warning(f"Le fichier '{reference_data_path}' existe déjà. Utilisez --force pour le recréer.")
        return

    if not full_dataset_path.exists():
        logger.error(f"Fichier source introuvable : '{full_dataset_path}'")
        sys.exit(1)

    try:
        df = pd.read_csv(full_dataset_path)
    except Exception as e:
        logger.error(f"Impossible de charger le dataset original : {e}")
        sys.exit(1)

    logger.info("Dataset chargé. Nettoyage et mapping des colonnes...")

    # Mapping CSV original → features utilisées par le modèle
    column_mapping = {
        "Temperature (?C)": "temperature",
        "Humidity (%)": "humidity",
        "CO2 (ppm)": "co2",
        "PM2.5 (?g/m?)": "pm25",
        "PM10 (?g/m?)": "pm10",
        "TVOC (ppb)": "tvoc",
        "Occupancy Count": "occupancy",
    }

    df = df.rename(columns=column_mapping)

    # Vérifier que toutes les colonnes nécessaires sont présentes
    missing_columns = [col for col in settings.FEATURE_COLUMNS if col not in df.columns]
    if missing_columns:
        logger.error(f"Colonnes manquantes dans le dataset original : {missing_columns}")
        sys.exit(1)

    # Filtrer uniquement les colonnes utiles
    df = df[settings.FEATURE_COLUMNS]

    # Création de la colonne 'target'
    df["target"] = df["occupancy"].apply(lambda x: 0 if x > 0 else 1)

    # Échantillonnage propre
    n_sample = min(settings.SAMPLE_SIZE, len(df))
    reference_df = df.sample(n=n_sample, random_state=42)

    # Sauvegarde du fichier final
    try:
        reference_data_path.parent.mkdir(parents=True, exist_ok=True)
        reference_df.to_csv(reference_data_path, index=False)
        logger.success(f"Fichier de référence créé : '{reference_data_path}' ({n_sample} lignes)")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier de référence : {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prépare le jeu de données de référence pour Evidently.")
    parser.add_argument("--force", action="store_true", help="Récrée le fichier même s'il existe.")
    args = parser.parse_args()
    create_reference_data(force=args.force)
