"""
Sauvegardes sécurisées de la base SQLite.
"""

from datetime import datetime
from pathlib import Path
import shutil
import sqlite3

from config import DATABASE_FILE, BACKUP_DIR

MAX_BACKUPS = 30


def create_backup(destination=None, prefix="facturation"):
    """Crée une sauvegarde SQLite cohérente et retourne son chemin."""
    source = Path(DATABASE_FILE)
    if not source.exists():
        raise FileNotFoundError("La base de données n'existe pas encore.")

    folder = Path(destination) if destination else Path(BACKUP_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{prefix}_{datetime.now():%Y%m%d_%H%M%S_%f}.db"

    source_conn = sqlite3.connect(source)
    target_conn = sqlite3.connect(target)
    try:
        with target_conn:
            source_conn.backup(target_conn)
    finally:
        target_conn.close()
        source_conn.close()

    prune_backups(folder)
    return target


def restore_backup(backup_path):
    """Restaure une sauvegarde après création d'un filet de sécurité."""
    source = Path(backup_path)
    target = Path(DATABASE_FILE)
    if not source.exists():
        raise FileNotFoundError("Le fichier de sauvegarde sélectionné est introuvable.")
    if source.resolve() == target.resolve():
        raise ValueError("La sauvegarde sélectionnée est déjà la base active.")

    if target.exists():
        create_backup(prefix="avant_restauration")

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def list_backups():
    folder = Path(BACKUP_DIR)
    folder.mkdir(parents=True, exist_ok=True)
    return sorted(folder.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)


def prune_backups(folder=None, keep=MAX_BACKUPS):
    """Conserve uniquement les N sauvegardes les plus récentes."""
    folder = Path(folder) if folder else Path(BACKUP_DIR)
    backups = sorted(folder.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old_backup in backups[keep:]:
        try:
            old_backup.unlink()
        except OSError:
            pass


def create_startup_backup():
    """Sauvegarde automatique au démarrage, avant toute migration éventuelle."""
    if not Path(DATABASE_FILE).exists():
        return None
    return create_backup(prefix="auto")


def create_import_backup():
    """Sauvegarde automatique juste avant un import Excel."""
    if not Path(DATABASE_FILE).exists():
        return None
    return create_backup(prefix="avant_import")
