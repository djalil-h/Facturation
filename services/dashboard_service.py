from sqlalchemy import func
from datetime import date, timedelta

from database.session import SessionLocal
from database.models import Facture, Fournisseur


class DashboardService:

    @staticmethod
    def get_dashboard_data():

        session = SessionLocal()

        try:

            total_factures = session.query(Facture).count()

            montant_total = (
                session.query(func.sum(Facture.montant))
                .scalar() or 0
            )

            montant_paye = (
                session.query(func.sum(Facture.montant))
                .filter(Facture.statut == "Payée")
                .scalar() or 0
            )

            reste = montant_total - montant_paye

            aujourd_hui = date.today()

            retard = (
                session.query(Facture)
                .filter(
                    Facture.statut != "Payée",
                    Facture.date_echeance < aujourd_hui
                )
                .count()
            )

            echeance = (
                session.query(Facture)
                .filter(
                    Facture.statut != "Payée",
                    Facture.date_echeance <= aujourd_hui + timedelta(days=7)
                )
                .count()
            )

            dernieres = (
                session.query(Facture)
                .order_by(Facture.id.desc())
                .limit(10)
                .all()
            )

            top_fournisseurs = (

                session.query(

                    Fournisseur.nom,

                    func.sum(Facture.montant)

                )

                .join(
                    Facture,
                    Fournisseur.id == Facture.fournisseur_id
                )

                .group_by(Fournisseur.nom)

                .order_by(
                    func.sum(Facture.montant).desc()
                )

                .limit(5)

                .all()

            )

            notifications = []

            if retard:

                notifications.append(

                    f"{retard} facture(s) en retard"

                )

            if echeance:

                notifications.append(

                    f"{echeance} facture(s) arrivent à échéance"

                )

            return {

                "total_factures": total_factures,

                "montant_total": montant_total,

                "montant_paye": montant_paye,

                "reste": reste,

                "retard": retard,

                "echeance": echeance,

                "dernieres": dernieres,

                "top_fournisseurs": top_fournisseurs,

                "notifications": notifications

            }

        finally:

            session.close()
