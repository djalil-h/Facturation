from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from database.db import get_session
from database.models import Facture, Fournisseur, StatutFacture


class DashboardService:
    """Business logic used by the dashboard."""

    @staticmethod
    def get_dashboard_data():
        session = get_session()
        try:
            total_factures = session.query(Facture).count()
            montant_total = session.query(func.coalesce(func.sum(Facture.montant), 0)).scalar() or 0
            montant_paye = session.query(func.coalesce(func.sum(Facture.montant_paye), 0)).scalar() or 0
            reste = max(0, montant_total - montant_paye)
            aujourd_hui = date.today()
            statut_payee = StatutFacture.PAYEE

            retard = (
                session.query(Facture)
                .filter(Facture.statut != statut_payee, Facture.date_echeance < aujourd_hui)
                .count()
            )
            echeance = (
                session.query(Facture)
                .filter(
                    Facture.statut != statut_payee,
                    Facture.date_echeance >= aujourd_hui,
                    Facture.date_echeance <= aujourd_hui + timedelta(days=7),
                )
                .count()
            )

            # The dashboard returns ORM invoices after this session is closed.
            # Eager loading prevents DetachedInstanceError when the view reads
            # facture.fournisseur.nom outside the session.
            dernieres = (
                session.query(Facture)
                .options(selectinload(Facture.fournisseur))
                .order_by(Facture.id.desc())
                .limit(10)
                .all()
            )

            top_fournisseurs = (
                session.query(
                    Fournisseur.nom,
                    func.sum(Facture.montant).label("montant_total"),
                )
                .join(Facture, Fournisseur.id == Facture.fournisseur_id)
                .group_by(Fournisseur.nom)
                .order_by(func.sum(Facture.montant).desc())
                .limit(5)
                .all()
            )

            notifications = []
            if retard:
                notifications.append(f"{retard} facture(s) en retard")
            if echeance:
                notifications.append(f"{echeance} facture(s) arrivent à échéance")

            return {
                "total_factures": total_factures,
                "montant_total": float(montant_total),
                "montant_paye": float(montant_paye),
                "reste": float(reste),
                "retard": retard,
                "echeance": echeance,
                "dernieres": dernieres,
                "top_fournisseurs": top_fournisseurs,
                "notifications": notifications,
            }
        finally:
            session.close()


def statistiques_generales():
    """Compatibility API used by the current dashboard view."""
    return DashboardService.get_dashboard_data()
