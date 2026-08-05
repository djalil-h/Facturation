"""
===========================================================
Facturation
Pharmacie Hamzaoui Hamid
Configuration générale
===========================================================
"""

from pathlib import Path

# ----------------------------------------------------------
# Informations de l'application
# ----------------------------------------------------------

APP_NAME = "Facturation"
PHARMACY_NAME = "Pharmacie Hamzaoui Hamid"
APP_VERSION = "1.0.0"

# ----------------------------------------------------------
# Répertoires
# ----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "facturation.db"

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
LOGO_DIR = ASSETS_DIR / "logo"

BACKUP_DIR = BASE_DIR / "backups"
EXPORT_DIR = BASE_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"

# ----------------------------------------------------------
# Couleurs (Style Windows 10)
# ----------------------------------------------------------

PRIMARY_COLOR = "#0078D7"
SECONDARY_COLOR = "#F3F3F3"
SUCCESS_COLOR = "#107C10"
WARNING_COLOR = "#FFB900"
DANGER_COLOR = "#D13438"
TEXT_COLOR = "#202020"
BACKGROUND_COLOR = "#FFFFFF"

# ----------------------------------------------------------
# Utilisateur administrateur
# ----------------------------------------------------------

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# ----------------------------------------------------------
# Création automatique des dossiers
# ----------------------------------------------------------

for folder in (
    DATABASE_DIR,
    BACKUP_DIR,
    EXPORT_DIR,
    LOG_DIR,
    ICONS_DIR,
    IMAGES_DIR,
    LOGO_DIR,
):
    folder.mkdir(parents=True, exist_ok=True)