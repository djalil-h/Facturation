from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from database.db import get_session
from database.models import Facture, Fournisseur, StatutFacture


class DashboardService:
    """Business logic used by the dashboard, including supplier credits."""

    @staticmethod
    def get_dashboard_data():
        session = get_session()
        try:
            toutes = session.query(Facture).options(selectinload(Facture.fournisseur)).all()
            factures_normales = [f for f in toutes if getattr(f, "type_piece", "Facture") != "Avoir"]
            avoirs = [f for f in toutes if getattr(f, "type_piece", "Facture") == "Avoir"]

            total_factures = len(factures_normales)
            montant_total = sum(float(f.montant or 0) for f in factures_normales)
            montant_paye = sum(float(f.montant_paye or 0) for f in factures_normales)
            dette_factures = sum(max(0.0, float(f.reste or 0)) for f in factures_normales)
            total_avoirs = sum(abs(float(f.montant or 0)) for f in avoirs)
            # Solde fournisseur = factures restant dues - avoirs disponibles.
            solde_global = dette_factures - total_avoirs

            aujourd_hui = date.today()
            limite_echeance = aujourd_hui + timedelta(days=7)
            impayees = [f for f in factures_normales if float(f.reste or 0) > 0]
            retard = sum(1 for f in impayees if f.date_echeance < aujourd_hui)
            echeance = sum(1 for f in impayees if aujourd_hui <= f.date_echeance <= limite_echeance)

            dernieres = (
                session.query(Facture)
                .options(selectinload(Facture.fournisseur))
                .order_by(Facture.id.desc()).limit(10).all()
            )
            echeances = sorted(
                [f for f in impayees if f.date_echeance <= limite_echeance],
                key=lambda f: (f.date_echeance, f.id),
            )[:10]

            dettes_map = {}
            for facture in toutes:
                fournisseur = facture.fournisseur
                fournisseur_id = fournisseur.id if fournisseur else facture.fournisseur_id
                fournisseur_nom = fournisseur.nom if fournisseur else "Fournisseur non renseigné"
                key = fournisseur_id or 0
                if key not in dettes_map:
                    dettes_map[key] = {
                        "fournisseur_id": fournisseur_id,
                        "fournisseur_nom": fournisseur_nom,
                        "nombre_factures": 0,
                        "nombre_avoirs": 0,
                        "montant_total": 0.0,
                        "montant_paye": 0.0,
                        "avoirs": 0.0,
                        "dette": 0.0,
                        "solde": 0.0,
                        "factures": [],
                    }
                groupe = dettes_map[key]
                if getattr(facture, "type_piece", "Facture") == "Avoir":
                    avoir = abs(float(facture.montant or 0))
                    groupe["nombre_avoirs"] += 1
                    groupe["avoirs"] += avoir
                    groupe["solde"] -= avoir
                    groupe["factures"].append({
                        "id": facture.id, "numero": facture.numero,
                        "date_facture": facture.date_facture, "date_echeance": facture.date_echeance,
                        "montant": -avoir, "montant_paye": 0.0, "reste": -avoir,
                        "statut": "Avoir", "type_piece": "Avoir",
                    })
                else:
                    montant = float(facture.montant or 0)
                    paye = float(facture.montant_paye or 0)
                    reste = max(0.0, float(facture.reste or 0))
                    groupe["nombre_factures"] += 1
                    groupe["montant_total"] += montant
                    groupe["montant_paye"] += paye
                    groupe["dette"] += reste
                    groupe["solde"] += reste
                    if reste > 0:
                        groupe["factures"].append({
                            "id": facture.id, "numero": facture.numero,
                            "date_facture": facture.date_facture, "date_echeance": facture.date_echeance,
                            "montant": montant, "montant_paye": paye, "reste": reste,
                            "statut": getattr(facture.statut, "value", facture.statut), "type_piece": "Facture",
                        })

            dettes_fournisseurs = sorted(
                [g for g in dettes_map.values() if abs(g["solde"]) > 0.0001],
                key=lambda item: (-item["solde"], item["fournisseur_nom"].lower()),
            )
            nombre_factures_impayees = len(impayees)
            nombre_fournisseurs_dettes = sum(1 for g in dettes_fournisseurs if g["solde"] > 0)

            top_fournisseurs = sorted(
                [(g["fournisseur_nom"], g["solde"]) for g in dettes_fournisseurs],
                key=lambda x: x[1], reverse=True,
            )[:5]

            notifications = []
            if retard:
                notifications.append(f"{retard} facture(s) en retard")
            if echeance:
                notifications.append(f"{echeance} facture(s) arrivent à échéance sous 7 jours")
            if nombre_fournisseurs_dettes:
                notifications.append(f"{nombre_fournisseurs_dettes} fournisseur(s) ont une dette en cours")
            credits = sum(1 for g in dettes_fournisseurs if g["solde"] < 0)
            if credits:
                notifications.append(f"{credits} fournisseur(s) ont un crédit/avoir disponible")

            return {
                "total_factures": total_factures,
                "montant_total": float(montant_total),
                "montant_paye": float(montant_paye),
                "reste": float(dette_factures),
                "dette_factures": float(dette_factures),
                "total_avoirs": float(total_avoirs),
                "solde_global": float(solde_global),
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
    return DashboardService.get_dashboard_data()
