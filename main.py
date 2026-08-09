from database import create_database
from services.backup_service import create_startup_backup
from services.user_service import create_admin

from UI.app import FacturationApp


def main():
    # Sauvegarder la base existante avant toute création/migration de schéma.
    create_startup_backup()

    create_database()
    create_admin()

    app = FacturationApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
