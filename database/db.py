"""
=========================================================
Facturation
Pharmacie Hamzaoui Hamid
db.py
=========================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_FILE
from database.models import Base

# Base SQLite
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Fabrique de sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)


def create_database():
    """
    Création automatique des tables.
    """
    Base.metadata.create_all(bind=engine)


def get_session():
    """
    Retourne une session SQLAlchemy.
    """
    return SessionLocal()