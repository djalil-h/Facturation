from datetime import date, timedelta

from sqlalchemy.orm import selectinload

from database.db import get_session
from database.models import Facture


class DashboardService:
    """Calculs du tableau de bord, avec prise en compte des avoirs fournisseurs."""

    @staticmethod
    def get_dashboard_data():
        session = get_session()
        try:
            toutes = session.query(Facture).options(selectinload(Facture.fournisseur)).all()

            factures_normales = [
                f for f in toutes
                if getattr(f, "type_piece", "Facture") != "Avoir"
            ]
            avoirs = [
                f for f in toutes
                if getattr(f, "type_piece", "Facture") == "Avoir"
            ]

            # Une dette réelle tient compte des paiements ET des avoirs.
            # Les avoirs sont toujours comptés en valeur positive dans le
            # calcul, car ils diminuent le solde fournisseur.
            montant_total = sum(float(f.montant or 0) for f in factures_normales)
            montant_paye = sum(float(f.montant_paye or 0) for f in factures_normales)
            dette_factures = sum(max(0.0, float(f.reste or 0)) for f in factures_normales)
            total_avoirs = sum(abs(float(f.montant or 0)) for f in avoirs)
            solde_global = dette_factures - total_avoirs

            aujourd_hui = date.today()
            limite_echeance = aujourd_hui + timedelta(days=7)
            impayees = [f for f in factures_normales if float(f.reste or 0) > 0]
            retard = sum(1 for f in impayees if f.date_echeance < aujourd_hui)
            echeance = sum(
                1 for f in impayees
                if aujourd_hui <= f.date_echeance <= limite_echeance
            )

            dernieres = (
                session.query(Facture)
                .options(selectinload(Facture.fournisseur))
                .order_by(Facture.id.desc())
                .limit(10)
                .all()
            )

            echeances = sorted(
                [f for f in impayees if f.date_echeance <= limite_echeance],
                key=lambda f: (f.date_echeance, f.id),
            )[:10]

            dettes_map = {}
            for piece in toutes:
                fournisseur = piece.fournisseur
                fournisseur_id = fournisseur.id if fournisseur else piece.fournisseur_id
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

                if getattr(piece, "type_piece", "Facture") == "Avoir":
                    avoir = abs(float(piece.montant or 0))
                    groupe["nombre_avoirs"] += 1
                    groupe["avoirs"] += avoir
                    groupe["solde"] -= avoir
                    groupe["factures"].append({
                        "id": piece.id,
                        "numero": piece.numero,
                        "date_facture": piece.date_facture,
                        "date_echeance": piece.date_echeance,
                        "montant": -avoir,
                        "montant_paye": 0.0,
                        "reste": -avoir,
                        "statut": "Avoir",
                        "type_piece": "Avoir",
                    })
                else:
                    montant = float(piece.montant or 0)
                    paye = float(piece.montant_paye or 0)
                    reste = max(0.0, float(piece.reste or 0))
                    groupe["nombre_factures"] += 1
                    groupe["montant_total"] += montant
                    groupe["montant_paye"] += paye
                    groupe["dette"] += reste
                    groupe["solde"] += reste

                    # Seules les factures avec un reste positif sont
                    # proposées dans la liste des impayées/règlements.
                    if reste > 0:
                        groupe["factures"].append({
                            "id": piece.id,
                            "numero": piece.numero,
                            "date_facture": piece.date_facture,
                            "date_echeance": piece.date_echeance,
                            "montant": montant,
                            "montant_paye": paye,
                            "reste": reste,
                            "statut": getattr(piece.statut, "value", piece.statut),
                            "type_piece": "Facture",
                        })

            # IMPORTANT : la dette affichée est le solde net après avoirs.
            # Elle peut être négative : dans ce cas le fournisseur nous doit
            # un crédit et ce n'est plus une dette à payer.
            for groupe in dettes_map.values():
                groupe["solde"] = groupe["dette"] - groupe["avoirs"]

            dettes_fournisseurs = sorted(
                [g for g in dettes_map.values() if abs(g["solde"]) > 0.0001],
                key=lambda item: (-item["solde"], item["fournisseur_nom"].lower()),
            )

            nombre_factures_impayees = len(impayees)
            nombre_fournisseurs_dettes = sum(
                1 for g in dettes_fournisseurs if g["solde"] > 0
            )

            top_fournisseurs = sorted(
                [(g["fournisseur_nom"], g["solde"]) for g in dettes_fournisseurs],
                key=lambda x: x[1],
                reverse=True,
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
                "total_factures": len(factures_normales),
                "montant_total": float(montant_total),
                "montant_paye": float(montant_paye),
                # Carte "Dette fournisseurs" = dette nette après avoirs.
                "reste": float(solde_global),
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
