import logging
import os
from app.services.evidently_service import evidently_service
from app.config import AppConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    logging.info(">>> Lancement du monitoring Evidently...")

    reference_path = AppConfig.REFERENCE_DATA_PATH
    reports_dir = AppConfig.REPORTS_DIR

    # Vérifier que le fichier de référence existe
    if not reference_path.exists():
        logging.error(f"Fichier de référence introuvable : {reference_path}")
        return

    # Vérifier que le dossier de rapports existe
    reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = evidently_service.update_all_reports()
        logging.info(f">>> Rapport généré : {result}")
    except FileNotFoundError as fe:
        logging.error(f"Fichier introuvable : {fe}")
    except Exception as e:
        logging.error(f"Erreur lors de la génération du rapport : {e}")

if __name__ == "__main__":
    main()
