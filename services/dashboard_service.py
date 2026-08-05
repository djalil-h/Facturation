from datetime import date, timedelta

from sqlalchemy import func

from database.db import get_session
from database.models import (
    Facture,
    Fournisseur,
    Notification,
    StatutFacture
)
def statistiques_generales():

    session = get_session()

    total_factures = session.query(Facture).count()

    montant_total = session.query(
        func.sum(Facture.montant)
    ).scalar() or 0

    montant_paye = session.query(
        func.sum(Facture.montant_paye)
    ).scalar() or 0

    reste = session.query(
        func.sum(Facture.reste)
    ).scalar() or 0

    impayees = session.query(Facture).filter(
        Facture.statut == StatutFacture.IMPAYEE
    ).count()

    partielles = session.query(Facture).filter(
        Facture.statut == StatutFacture.PARTIELLE
    ).count()

    payees = session.query(Facture).filter(
        Facture.statut == StatutFacture.PAYEE
    ).count()

    session.close()

    return {
        "total_factures": total_factures,
        "montant_total": montant_total,
        "montant_paye": montant_paye,
        "reste": reste,
        "impayees": impayees,
        "partielles": partielles,
        "payees": payees
    }
def factures_en_retard():

    session = get_session()

    aujourd_hui = date.today()

    resultat = (
        session.query(Facture)
        .filter(
            Facture.date_echeance < aujourd_hui,
            Facture.statut != StatutFacture.PAYEE
        )
        .all()
    )

    session.close()

    return resultat
def echeances_prochaines():

    session = get_session()

    aujourd_hui = date.today()

    limite = aujourd_hui + timedelta(days=7)

    resultat = (
        session.query(Facture)
        .filter(
            Facture.date_echeance >= aujourd_hui,
            Facture.date_echeance <= limite,
            Facture.statut != StatutFacture.PAYEE
        )
        .all()
    )

    session.close()

    return resultat
def statistiques_fournisseurs():

    session = get_session()

    data = []

    fournisseurs = session.query(Fournisseur).all()

    for fournisseur in fournisseurs:

        total = sum(f.montant for f in fournisseur.factures)

        paye = sum(f.montant_paye for f in fournisseur.factures)

        reste = sum(f.reste for f in fournisseur.factures)

        data.append({
            "nom": fournisseur.nom,
            "total": total,
            "paye": paye,
            "reste": reste
        })

    session.close()

    return data
def generer_notifications():

    session = get_session()

    session.query(Notification).delete()

    aujourd_hui = date.today()

    retard = session.query(Facture).filter(
        Facture.date_echeance < aujourd_hui,
        Facture.statut != StatutFacture.PAYEE
    ).count()

    if retard:

        session.add(
            Notification(
                titre="Factures en retard",
                message=f"{retard} facture(s) sont en retard."
            )
        )

    proche = session.query(Facture).filter(
        Facture.date_echeance <= aujourd_hui + timedelta(days=7),
        Facture.date_echeance >= aujourd_hui,
        Facture.statut != StatutFacture.PAYEE
    ).count()

    if proche:

        session.add(
            Notification(
                titre="Échéances",
                message=f"{proche} facture(s) arrivent à échéance."
            )
        )

    session.commit()

    session.close()
