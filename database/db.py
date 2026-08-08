"""
=========================================================
Facturation
Pharmacie Hamzaoui Hamid
db.py
=========================================================
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from config import DATABASE_FILE
from database.models import Base

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _migrate_factures_for_avoirs():
    """Upgrade an existing SQLite database to support signed supplier credits.

    Older versions had CHECK(montant >= 0). SQLite cannot remove a CHECK
    constraint with ALTER TABLE, so the factures table is rebuilt only when
    the old schema is detected. Existing rows and IDs are preserved.
    """
    inspector = inspect(engine)
    if "factures" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("factures")}
    table_sql = engine.connect().execute(
        text("SELECT sql FROM sqlite_master WHERE type='table' AND name='factures'")
    ).scalar() or ""
    needs_type = "type_piece" not in columns
    old_positive_constraint = "montant>=0" in table_sql.replace(" ", "").lower()
    if not needs_type and not old_positive_constraint:
        return

    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        conn.execute(text("ALTER TABLE factures RENAME TO factures_old"))
        conn.execute(text("""
            CREATE TABLE factures (
                id INTEGER NOT NULL PRIMARY KEY,
                numero VARCHAR(100) NOT NULL UNIQUE,
                fournisseur_id INTEGER,
                date_facture DATE NOT NULL,
                date_echeance DATE NOT NULL,
                montant FLOAT NOT NULL,
                montant_paye FLOAT DEFAULT 0,
                reste FLOAT NOT NULL,
                statut VARCHAR(18) NOT NULL,
                type_piece VARCHAR(20) NOT NULL DEFAULT 'Facture',
                commentaire TEXT,
                created_by INTEGER,
                created_at DATETIME,
                updated_at DATETIME,
                CONSTRAINT chk_montant_paye CHECK (montant_paye >= 0),
                CONSTRAINT chk_reste CHECK (reste >= 0 OR type_piece = 'Avoir'),
                CONSTRAINT uq_numero_facture UNIQUE (numero),
                FOREIGN KEY(fournisseur_id) REFERENCES fournisseurs (id),
                FOREIGN KEY(created_by) REFERENCES users (id)
            )
        """))
        old_columns = {column["name"] for column in inspector.get_columns("factures_old")}
        type_expr = "'Facture'" if "type_piece" not in old_columns else "COALESCE(type_piece, 'Facture')"
        conn.execute(text(f"""
            INSERT INTO factures (
                id, numero, fournisseur_id, date_facture, date_echeance,
                montant, montant_paye, reste, statut, type_piece,
                commentaire, created_by, created_at, updated_at
            )
            SELECT id, numero, fournisseur_id, date_facture, date_echeance,
                   montant, montant_paye, reste, statut, {type_expr},
                   commentaire, created_by, created_at, updated_at
            FROM factures_old
        """))
        conn.execute(text("DROP TABLE factures_old"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_facture_numero ON factures (numero)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_facture_statut ON factures (statut)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_facture_date ON factures (date_facture)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_facture_fournisseur ON factures (fournisseur_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_facture_type_piece ON factures (type_piece)"))
        conn.execute(text("PRAGMA foreign_keys=ON"))


def create_database():
    Base.metadata.create_all(bind=engine)
    _migrate_factures_for_avoirs()
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
