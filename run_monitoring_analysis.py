from pathlib import Path
from loguru import logger
from app.services.evidently_service import evidently_service
from app.config import get_settings


def main() -> None:
    """
    Exécute le monitoring Evidently :
    - Vérifie la présence des fichiers de référence
    - Génère les rapports de dérive et de performance
    - Met à jour les métriques Prometheus
    """
    settings = get_settings()
    reference_path: Path = settings.REFERENCE_DATA_PATH
    reports_dir: Path = settings.REPORTS_DIR

    logger.info(">>> Lancement du monitoring Evidently...")

    if not reference_path.exists():
        logger.error(f"Fichier de référence introuvable : {reference_path}")
        return

    # S'assurer que le dossier de rapports existe
    reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = evidently_service.update_all_reports()
        logger.success(f">>> Rapport Evidently généré : {result}")
    except FileNotFoundError as fe:
        logger.error(f"Fichier introuvable : {fe}")
    except Exception as e:
        logger.exception(f"Erreur lors de la génération des rapports Evidently : {e}")


if __name__ == "__main__":
    main()
