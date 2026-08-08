from datetime import date

from sqlalchemy.orm import selectinload

from database.db import get_session
from database.models import (
    Facture,
    Fournisseur,
    Paiement,
    Historique,
    StatutFacture,
)


def _recalculer_statut(facture):
    """Keep amount, remaining balance and invoice status consistent."""
    facture.montant_paye = max(0, facture.montant_paye or 0)
    facture.reste = max(0, facture.montant - facture.montant_paye)

    if facture.reste == 0:
        facture.statut = StatutFacture.PAYEE
    elif facture.montant_paye > 0:
        facture.statut = StatutFacture.PARTIELLE
    else:
        facture.statut = StatutFacture.IMPAYEE


def _user_id(utilisateur):
    return getattr(utilisateur, "id", None)


def _username(utilisateur):
    return getattr(utilisateur, "username", "Invité")


def ajouter_facture(numero, fournisseur_id, date_facture, date_echeance, montant, commentaire, utilisateur):
    session = get_session()
    try:
        existe = session.query(Facture).filter_by(numero=numero).first()
        if existe:
            raise ValueError("Numéro de facture déjà utilisé.")

        facture = Facture(
            numero=numero,
            fournisseur_id=fournisseur_id,
            date_facture=date_facture,
            date_echeance=date_echeance,
            montant=montant,
            montant_paye=0,
            reste=montant,
            statut=StatutFacture.IMPAYEE,
            commentaire=commentaire,
            created_by=_user_id(utilisateur),
        )
        session.add(facture)
        session.flush()
        session.add(Historique(
            facture_id=facture.id,
            action="Création",
            details=f"Facture {numero} créée.",
            utilisateur=_username(utilisateur),
        ))
        session.commit()
        session.refresh(facture)
        # The caller receives the ORM object after the session is closed.
        # Eagerly load the supplier so UI code can safely read facture.fournisseur.
        facture.fournisseur
        return facture
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def liste_factures():
    session = get_session()
    try:
        return (
            session.query(Facture)
            .options(selectinload(Facture.fournisseur))
            .order_by(Facture.date_facture.desc())
            .all()
        )
    finally:
        session.close()


def supprimer_facture(facture_id):
    session = get_session()
    try:
        facture = session.get(Facture, facture_id)
        if facture:
            session.delete(facture)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def modifier_facture(facture_id, fournisseur_id, numero, date_facture, date_echeance, montant, commentaire, utilisateur):
    session = get_session()
    try:
        facture = session.get(Facture, facture_id)
        if facture is None:
            return False

        duplicate = (
            session.query(Facture)
            .filter(Facture.numero == numero, Facture.id != facture_id)
            .first()
        )
        if duplicate:
            raise ValueError("Numéro de facture déjà utilisé.")

        facture.numero = numero
        facture.fournisseur_id = fournisseur_id
        facture.date_facture = date_facture
        facture.date_echeance = date_echeance
        facture.commentaire = commentaire
        facture.montant = montant
        _recalculer_statut(facture)
        session.add(Historique(
            facture_id=facture.id,
            action="Modification",
            details=f"Facture {numero} modifiée",
            utilisateur=_username(utilisateur),
        ))
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ajouter_paiement(facture_id, montant, mode, reference, utilisateur):
    session = get_session()
    try:
        facture = session.get(Facture, facture_id)
        if facture is None:
            raise ValueError("Facture introuvable.")
        if montant <= 0:
            raise ValueError("Montant invalide.")
        if montant > facture.reste:
            raise ValueError("Le paiement dépasse le reste à payer.")

        paiement = Paiement(
            facture_id=facture.id,
            montant=montant,
            date_paiement=date.today(),
            mode_paiement=mode,
            reference=reference,
            utilisateur_id=_user_id(utilisateur),
        )
        facture.montant_paye += montant
        _recalculer_statut(facture)
        session.add(paiement)
        session.add(Historique(
            facture_id=facture.id,
            action="Paiement",
            details=f"Paiement de {montant:.2f} DA",
            utilisateur=_username(utilisateur),
        ))
        session.commit()
        return paiement
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def liste_paiements(facture_id):
    session = get_session()
    try:
        return (
            session.query(Paiement)
            .filter_by(facture_id=facture_id)
            .order_by(Paiement.date_paiement.desc())
            .all()
        )
    finally:
        session.close()


def rechercher_factures(fournisseur_id=None, statut=None, date_debut=None, date_fin=None):
    session = get_session()
    try:
        query = session.query(Facture).options(selectinload(Facture.fournisseur))
        if fournisseur_id:
            query = query.filter(Facture.fournisseur_id == fournisseur_id)
        if statut:
            if isinstance(statut, str):
                try:
                    statut = StatutFacture(statut)
                except ValueError:
                    try:
                        statut = StatutFacture[statut]
                    except KeyError:
                        return []
            query = query.filter(Facture.statut == statut)
        if date_debut:
            query = query.filter(Facture.date_facture >= date_debut)
        if date_fin:
            query = query.filter(Facture.date_facture <= date_fin)
        return query.order_by(Facture.date_facture.desc()).all()
    finally:
        session.close()
