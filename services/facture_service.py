from datetime import date

from sqlalchemy import and_

from database.db import get_session
from database.models import (
    Facture,
    Fournisseur,
    Paiement,
    Historique,
    StatutFacture
)
# =========================================================
# AJOUT FACTURE
# =========================================================

def ajouter_facture(
    numero,
    fournisseur_id,
    date_facture,
    date_echeance,
    montant,
    commentaire,
    utilisateur
):

    session = get_session()

    existe = (
        session.query(Facture)
        .filter_by(numero=numero)
        .first()
    )

    if existe:
        session.close()
        raise Exception("Numéro de facture déjà utilisé.")

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
        created_by=utilisateur.id
    )

    session.add(facture)

    session.flush()

    historique = Historique(
        facture_id=facture.id,
        action="Création",
        details=f"Facture {numero} créée.",
        utilisateur=utilisateur.username
    )

    session.add(historique)

    session.commit()

    session.refresh(facture)

    session.close()

    return facture
# =========================================================
# LISTE
# =========================================================

def liste_factures():

    session = get_session()

    factures = (
        session.query(Facture)
        .order_by(Facture.date_facture.desc())
        .all()
    )

    session.close()

    return factures
# =========================================================
# SUPPRESSION
# =========================================================

def supprimer_facture(facture_id):

    session = get_session()

    facture = session.get(Facture, facture_id)

    if facture:

        session.delete(facture)

        session.commit()

    session.close()

# =========================================================
# MODIFIER UNE FACTURE
# =========================================================

def modifier_facture(
    facture_id,
    fournisseur_id,
    numero,
    date_facture,
    date_echeance,
    montant,
    commentaire,
    utilisateur
):

    session = get_session()

    facture = session.get(Facture, facture_id)

    if facture is None:
        session.close()
        return False

    ancien_montant = facture.montant

    facture.numero = numero
    facture.fournisseur_id = fournisseur_id
    facture.date_facture = date_facture
    facture.date_echeance = date_echeance
    facture.commentaire = commentaire
    facture.montant = montant

    difference = montant - ancien_montant
    facture.reste += difference

    if facture.reste <= 0:
        facture.reste = 0
        facture.statut = StatutFacture.PAYEE

    elif facture.reste < facture.montant:
        facture.statut = StatutFacture.PARTIELLE

    else:
        facture.statut = StatutFacture.IMPAYEE

    session.add(
        Historique(
            facture_id=facture.id,
            action="Modification",
            details=f"Facture {numero} modifiée",
            utilisateur=utilisateur.username
        )
    )

    session.commit()

    session.close()

    return True
# =========================================================
# ENREGISTRER UN PAIEMENT
# =========================================================

def ajouter_paiement(
    facture_id,
    montant,
    mode,
    reference,
    utilisateur
):

    session = get_session()

    facture = session.get(Facture, facture_id)

    if facture is None:
        session.close()
        raise Exception("Facture introuvable.")

    if montant <= 0:
        session.close()
        raise Exception("Montant invalide.")

    if montant > facture.reste:
        session.close()
        raise Exception("Le paiement dépasse le reste à payer.")

    paiement = Paiement(
        facture_id=facture.id,
        montant=montant,
        date_paiement=date.today(),
        mode_paiement=mode,
        reference=reference,
        utilisateur_id=utilisateur.id
    )

    facture.montant_paye += montant
    facture.reste -= montant

    if facture.reste == 0:
        facture.statut = StatutFacture.PAYEE

    elif facture.montant_paye > 0:
        facture.statut = StatutFacture.PARTIELLE

    session.add(paiement)

    session.add(
        Historique(
            facture_id=facture.id,
            action="Paiement",
            details=f"Paiement de {montant:.2f} DA",
            utilisateur=utilisateur.username
        )
    )

    session.commit()

    session.close()
# =========================================================
# LISTE DES PAIEMENTS
# =========================================================

def liste_paiements(facture_id):

    session = get_session()

    paiements = (
        session.query(Paiement)
        .filter_by(facture_id=facture_id)
        .order_by(Paiement.date_paiement.desc())
        .all()
    )

    session.close()

    return paiements
# =========================================================
# RECHERCHE MULTICRITÈRES
# =========================================================

def rechercher_factures(
    fournisseur_id=None,
    statut=None,
    date_debut=None,
    date_fin=None
):

    session = get_session()

    query = session.query(Facture)

    if fournisseur_id:
        query = query.filter(
            Facture.fournisseur_id == fournisseur_id
        )

    if statut:
        query = query.filter(
            Facture.statut == statut
        )

    if date_debut:
        query = query.filter(
            Facture.date_facture >= date_debut
        )

    if date_fin:
        query = query.filter(
            Facture.date_facture <= date_fin
        )

    resultats = (
        query.order_by(Facture.date_facture.desc())
        .all()
    )

    session.close()

    return resultats
