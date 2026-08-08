from datetime import datetime
from pathlib import Path
import shutil

from config import DATABASE_FILE, BACKUP_DIR


def create_backup(destination=None):
    """Crée une copie de la base SQLite et retourne son chemin."""
    source = Path(DATABASE_FILE)
    if not source.exists():
        raise FileNotFoundError("La base de données n'existe pas encore.")

    folder = Path(destination) if destination else Path(BACKUP_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"facturation_{datetime.now():%Y%m%d_%H%M%S}.db"
    shutil.copy2(source, target)
    return target


def restore_backup(backup_path):
    """Remplace la base actuelle par une sauvegarde."""
    source = Path(backup_path)
    target = Path(DATABASE_FILE)
    if not source.exists():
        raise FileNotFoundError("Le fichier de sauvegarde sélectionné est introuvable.")
    if source.resolve() == target.resolve():
        raise ValueError("La sauvegarde sélectionnée est déjà la base active.")

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def list_backups():
    folder = Path(BACKUP_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    return sorted(folder.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
