"""
=========================================================
Facturation
Pharmacie Hamzaoui Hamid
models.py
=========================================================
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, Enum, UniqueConstraint, CheckConstraint, Index
import enum
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class StatutFacture(enum.Enum):
    IMPAYEE = "Impayée"
    PARTIELLE = "Partiellement payée"
    PAYEE = "Payée"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    factures = relationship("Facture", back_populates="createur")
    paiements = relationship("Paiement", back_populates="utilisateur")

class Fournisseur(Base):
    __tablename__ = "fournisseurs"
    id = Column(Integer, primary_key=True)
    nom = Column(String(150), nullable=False)
    contact = Column(String(150))
    telephone = Column(String(30))
    email = Column(String(150))
    adresse = Column(Text)
    ville = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    factures = relationship("Facture", back_populates="fournisseur")

class Facture(Base):
    __tablename__ = "factures"
    id = Column(Integer, primary_key=True)
    numero = Column(String(100), unique=True, nullable=False)
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"))
    date_facture = Column(Date, nullable=False)
    date_echeance = Column(Date, nullable=False)
    # Facture = montant positif ; Avoir = montant négatif.
    montant = Column(Float, nullable=False)
    montant_paye = Column(Float, default=0)
    reste = Column(Float, nullable=False)
    statut = Column(Enum(StatutFacture), default=StatutFacture.IMPAYEE, nullable=False)
    type_piece = Column(String(20), default="Facture", nullable=False)
    historique = relationship("Historique", back_populates="facture", cascade="all, delete-orphan")
    commentaire = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime)
    fournisseur = relationship("Fournisseur", back_populates="factures")
    createur = relationship("User", back_populates="factures")
    paiements = relationship("Paiement", back_populates="facture", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint("numero", name="uq_numero_facture"),
        CheckConstraint("montant_paye>=0", name="chk_montant_paye"),
        CheckConstraint("reste>=0 OR type_piece='Avoir'", name="chk_reste"),
        Index("idx_facture_numero", "numero"),
        Index("idx_facture_statut", "statut"),
        Index("idx_facture_date", "date_facture"),
        Index("idx_facture_fournisseur", "fournisseur_id"),
        Index("idx_facture_type_piece", "type_piece"),
    )

class Paiement(Base):
    __tablename__ = "paiements"
    id = Column(Integer, primary_key=True)
    facture_id = Column(Integer, ForeignKey("factures.id"))
    montant = Column(Float, nullable=False)
    date_paiement = Column(Date, nullable=False)
    mode_paiement = Column(String(50))
    reference = Column(String(100))
    utilisateur_id = Column(Integer, ForeignKey("users.id"))
    facture = relationship("Facture", back_populates="paiements")
    utilisateur = relationship("User", back_populates="paiements")

class Historique(Base):
    __tablename__ = "historique"
    id = Column(Integer, primary_key=True)
    facture_id = Column(Integer, ForeignKey("factures.id"))
    action = Column(String(100), nullable=False)
    details = Column(Text)
    utilisateur = Column(String(100))
    date_action = Column(DateTime, default=datetime.now)
    facture = relationship("Facture", back_populates="historique")

class JournalAction(Base):
    __tablename__ = "journal_actions"
    id = Column(Integer, primary_key=True)
    action = Column(String(100))
    description = Column(Text)
    utilisateur = Column(String(100))
    date_action = Column(DateTime, default=datetime.now)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    titre = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    lu = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
