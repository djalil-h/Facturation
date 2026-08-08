from datetime import date

from database.db import get_session
from database.models import Facture, Paiement, Historique, StatutFacture


def _is_avoir(piece):
    return str(getattr(piece, "type_piece", "Facture")).strip().lower() == "avoir"


def _user_id(utilisateur):
    return getattr(utilisateur, "id", None)


def _username(utilisateur):
    return getattr(utilisateur, "username", "Invité")


def regler_selection_factures_avoirs(facture_ids, avoir_ids, mode, reference, utilisateur):
    """Règle les factures sélectionnées en imputant uniquement les avoirs sélectionnés."""
    if not mode or not str(mode).strip():
        raise ValueError("Le mode de paiement est obligatoire.")
    if reference is not None and len(str(reference).strip()) > 100:
        raise ValueError("La référence du paiement ne peut pas dépasser 100 caractères.")

    facture_ids = list(dict.fromkeys(facture_ids or []))
    avoir_ids = list(dict.fromkeys(avoir_ids or []))
    if not facture_ids:
        raise ValueError("Sélectionnez au moins une facture à régler.")

    session = get_session()
    try:
        factures = (
            session.query(Facture)
            .filter(Facture.id.in_(facture_ids))
            .order_by(Facture.id.asc())
            .with_for_update()
            .all()
        )
        avoirs = (
            session.query(Facture)
            .filter(Facture.id.in_(avoir_ids))
            .order_by(Facture.id.asc())
            .with_for_update()
            .all()
        ) if avoir_ids else []

        if len(factures) != len(facture_ids):
            raise ValueError("Une ou plusieurs factures sélectionnées sont introuvables.")
        if len(avoirs) != len(avoir_ids):
            raise ValueError("Un ou plusieurs avoirs sélectionnés sont introuvables.")
        if any(_is_avoir(f) for f in factures):
            raise ValueError("Un avoir ne peut pas être sélectionné comme facture à régler.")
        if any(not _is_avoir(a) for a in avoirs):
            raise ValueError("La sélection contient une pièce qui n'est pas un avoir.")

        fournisseur_ids = {f.fournisseur_id for f in factures}
        if len(fournisseur_ids) != 1:
            raise ValueError("Le règlement groupé doit concerner un seul fournisseur.")
        fournisseur_id = next(iter(fournisseur_ids))
        if any(a.fournisseur_id != fournisseur_id for a in avoirs):
            raise ValueError("Les avoirs sélectionnés doivent appartenir au même fournisseur que les factures.")
        if any(float(f.reste or 0) <= 0 for f in factures):
            raise ValueError("Toutes les factures sélectionnées doivent avoir un reste à payer.")
        if any(float(a.reste or 0) >= 0 for a in avoirs):
            raise ValueError("Tous les avoirs sélectionnés sont déjà entièrement imputés.")

        total_avant_avoir = sum(float(f.reste or 0) for f in factures)
        credit_selectionne = sum(abs(float(a.reste or 0)) for a in avoirs)
        credit_a_imputer = min(total_avant_avoir, credit_selectionne)

        imputations = []
        remaining_credit = {a.id: abs(float(a.reste or 0)) for a in avoirs}
        total_impute = 0.0

        for facture in factures:
            reste_facture = float(facture.reste or 0)
            for avoir in avoirs:
                credit = remaining_credit[avoir.id]
                if reste_facture <= 0 or credit <= 0:
                    continue
                montant = min(reste_facture, credit)
                facture.reste = max(0.0, reste_facture - montant)
                reste_facture = float(facture.reste)
                remaining_credit[avoir.id] = credit - montant
                avoir.reste = -remaining_credit[avoir.id]
                facture.statut = StatutFacture.PAYEE if facture.reste == 0 else (
                    StatutFacture.PARTIELLE if float(facture.montant_paye or 0) > 0 else StatutFacture.IMPAYEE
                )
                total_impute += montant
                imputations.append({"avoir": avoir.numero, "facture": facture.numero, "montant": montant})
                session.add(Historique(
                    facture_id=facture.id,
                    action="Imputation avoir",
                    details=f"Avoir {avoir.numero} imputé pour {montant:.2f} DA sur la facture {facture.numero}.",
                    utilisateur=_username(utilisateur),
                ))
                session.add(Historique(
                    facture_id=avoir.id,
                    action="Imputation avoir",
                    details=f"{montant:.2f} DA imputés sur la facture {facture.numero}.",
                    utilisateur=_username(utilisateur),
                ))

        paiements = []
        total_paye = 0.0
        for facture in factures:
            reste = float(facture.reste or 0)
            if reste <= 0:
                continue
            paiement = Paiement(
                facture_id=facture.id,
                montant=reste,
                date_paiement=date.today(),
                mode_paiement=str(mode).strip(),
                reference=(str(reference).strip() if reference else None),
                utilisateur_id=_user_id(utilisateur),
            )
            facture.montant_paye += reste
            facture.reste = 0.0
            facture.statut = StatutFacture.PAYEE
            session.add(paiement)
            session.add(Historique(
                facture_id=facture.id,
                action="Paiement groupé",
                details=f"Facture {facture.numero} réglée après imputation des avoirs sélectionnés : {reste:.2f} DA.",
                utilisateur=_username(utilisateur),
            ))
            paiements.append(paiement)
            total_paye += reste

        session.commit()
        return {
            "factures": len(factures),
            "paiements": paiements,
            "total": total_paye,
            "total_avant_avoir": total_avant_avoir,
            "avoir_selectionne": credit_selectionne,
            "avoir_impute": total_impute,
            "avoir_non_utilise": max(0.0, credit_selectionne - total_impute),
            "imputations": imputations,
            "credit_a_imputer": credit_a_imputer,
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
