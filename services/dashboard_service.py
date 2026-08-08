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
            limite_echeance = aujourd_hui + timedelta(days=7)

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
                    Facture.date_echeance <= limite_echeance,
                )
                .count()
            )

            dernieres = (
                session.query(Facture)
                .options(selectinload(Facture.fournisseur))
                .order_by(Facture.id.desc())
                .limit(10)
                .all()
            )

            echeances = (
                session.query(Facture)
                .options(selectinload(Facture.fournisseur))
                .filter(Facture.statut != statut_payee)
                .filter(Facture.date_echeance <= limite_echeance)
                .order_by(Facture.date_echeance.asc(), Facture.id.asc())
                .limit(10)
                .all()
            )

            # Main dashboard view: debt grouped by supplier, with every
            # unpaid/partially-paid invoice kept as plain dictionaries so the
            # UI never depends on a closed SQLAlchemy session.
            factures_impayees = (
                session.query(Facture)
                .options(selectinload(Facture.fournisseur))
                .filter(Facture.statut != statut_payee, Facture.reste > 0)
                .order_by(Fournisseur.nom.asc(), Facture.date_echeance.asc(), Facture.id.asc())
                .all()
            )

            dettes_map = {}
            for facture in factures_impayees:
                fournisseur = facture.fournisseur
                fournisseur_id = fournisseur.id if fournisseur else facture.fournisseur_id
                fournisseur_nom = fournisseur.nom if fournisseur else "Fournisseur non renseigné"
                key = fournisseur_id or 0

                if key not in dettes_map:
                    dettes_map[key] = {
                        "fournisseur_id": fournisseur_id,
                        "fournisseur_nom": fournisseur_nom,
                        "nombre_factures": 0,
                        "montant_total": 0.0,
                        "montant_paye": 0.0,
                        "dette": 0.0,
                        "factures": [],
                    }

                groupe = dettes_map[key]
                montant = float(facture.montant or 0)
                montant_paye_facture = float(facture.montant_paye or 0)
                reste_facture = max(0.0, float(facture.reste or 0))

                groupe["nombre_factures"] += 1
                groupe["montant_total"] += montant
                groupe["montant_paye"] += montant_paye_facture
                groupe["dette"] += reste_facture
                groupe["factures"].append({
                    "id": facture.id,
                    "numero": facture.numero,
                    "date_facture": facture.date_facture,
                    "date_echeance": facture.date_echeance,
                    "montant": montant,
                    "montant_paye": montant_paye_facture,
                    "reste": reste_facture,
                    "statut": getattr(facture.statut, "value", facture.statut),
                })

            dettes_fournisseurs = sorted(
                dettes_map.values(),
                key=lambda item: (-item["dette"], item["fournisseur_nom"].lower()),
            )

            nombre_factures_impayees = len(factures_impayees)
            nombre_fournisseurs_dettes = len(dettes_fournisseurs)

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
                notifications.append(f"{echeance} facture(s) arrivent à échéance sous 7 jours")
            if nombre_fournisseurs_dettes:
                notifications.append(
                    f"{nombre_fournisseurs_dettes} fournisseur(s) ont une dette en cours"
                )

            return {
                "total_factures": total_factures,
                "montant_total": float(montant_total),
                "montant_paye": float(montant_paye),
                "reste": float(reste),
                "retard": retard,
                "echeance": echeance,
                "dernieres": dernieres,
                "echeances": echeances,
                "dettes_fournisseurs": dettes_fournisseurs,
                "nombre_factures_impayees": nombre_factures_impayees,
                "nombre_fournisseurs_dettes": nombre_fournisseurs_dettes,
                "top_fournisseurs": top_fournisseurs,
                "notifications": notifications,
            }
        finally:
            session.close()


def statistiques_generales():
    """Compatibility API used by the current dashboard view."""
    return DashboardService.get_dashboard_data()
