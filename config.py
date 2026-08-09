"""
===========================================================
Hamzaoui Facturation
Pharmacie Hamzaoui Hamid
Configuration générale
===========================================================
"""

import os
import sys
from pathlib import Path

# ----------------------------------------------------------
# Informations de l'application
# ----------------------------------------------------------

APP_NAME = "Hamzaoui Facturation"
PHARMACY_NAME = "Pharmacie Hamzaoui Hamid"
APP_VERSION = "1.0.0"

# ----------------------------------------------------------
# Répertoires ressources / données
# ----------------------------------------------------------

# En développement, les ressources vivent dans le dépôt.
# En version PyInstaller, elles sont embarquées dans le dossier de ressources.
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    # Les données de production ne doivent jamais être écrites dans Program Files.
    DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Hamzaoui Facturation"
else:
    RESOURCE_DIR = Path(__file__).resolve().parent
    DATA_DIR = RESOURCE_DIR

BASE_DIR = RESOURCE_DIR

DATABASE_DIR = DATA_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "facturation.db"

ASSETS_DIR = RESOURCE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
LOGO_DIR = ASSETS_DIR / "logo"

BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = DATA_DIR / "logs"

ICON_FILE = ASSETS_DIR / "hamzaoui_logo.ico"
LOGO_FILE = ASSETS_DIR / "hamzaoui_logo.svg"

# ----------------------------------------------------------
# Couleurs
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
