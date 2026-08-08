from datetime import date

from sqlalchemy.orm import selectinload

from database.db import get_session
from database.models import Facture, Fournisseur, Paiement, Historique, StatutFacture


def _is_avoir(facture_or_type):
    value = facture_or_type if isinstance(facture_or_type, str) else getattr(facture_or_type, "type_piece", "Facture")
    return str(value).strip().lower() == "avoir"


def _recalculer_statut(facture):
    if _is_avoir(facture):
        facture.montant_paye = 0
        facture.reste = facture.montant
        facture.statut = StatutFacture.PAYEE
        return
    facture.montant_paye = max(0, float(facture.montant_paye or 0))
    facture.reste = max(0, float(facture.montant or 0) - facture.montant_paye)
    if facture.reste == 0:
        facture.statut = StatutFacture.PAYEE
    elif facture.montant_paye > 0:
        facture.statut = StatutFacture.PARTIELLE
    else:
        facture.statut = StatutFacture.IMPAYEE


def _validate_invoice_dates_and_amount(date_facture, date_echeance, montant):
    if montant is None or montant <= 0:
        raise ValueError("Le montant doit être strictement supérieur à zéro.")
    if date_facture is None or date_echeance is None:
        raise ValueError("Les dates de facture et d'échéance sont obligatoires.")
    if date_echeance < date_facture:
        raise ValueError("La date d'échéance ne peut pas être avant la date de facture.")


def _validate_payment_metadata(mode, reference):
    if not mode or not str(mode).strip():
        raise ValueError("Le mode de paiement est obligatoire.")
    if reference is not None and len(str(reference).strip()) > 100:
        raise ValueError("La référence du paiement ne peut pas dépasser 100 caractères.")


def _user_id(utilisateur):
    return getattr(utilisateur, "id", None)


def _username(utilisateur):
    return getattr(utilisateur, "username", "Invité")


def ajouter_facture(numero, fournisseur_id, date_facture, date_echeance, montant, commentaire, utilisateur, type_piece="Facture"):
    _validate_invoice_dates_and_amount(date_facture, date_echeance, montant)
    type_piece = "Avoir" if _is_avoir(type_piece) else "Facture"
    signed_amount = -abs(float(montant)) if type_piece == "Avoir" else abs(float(montant))
    session = get_session()
    try:
        if session.query(Facture).filter_by(numero=numero).first():
            raise ValueError("Numéro de facture déjà utilisé.")
        facture = Facture(numero=numero, fournisseur_id=fournisseur_id, date_facture=date_facture,
                          date_echeance=date_echeance, montant=signed_amount,
                          montant_paye=0, reste=signed_amount if type_piece == "Avoir" else abs(float(montant)),
                          statut=StatutFacture.PAYEE if type_piece == "Avoir" else StatutFacture.IMPAYEE,
                          type_piece=type_piece, commentaire=commentaire, created_by=_user_id(utilisateur))
        session.add(facture)
        session.flush()
        libelle = "Avoir" if type_piece == "Avoir" else "Facture"
        session.add(Historique(facture_id=facture.id, action="Création",
                               details=f"{libelle} {numero} créée.", utilisateur=_username(utilisateur)))
        session.commit()
        session.refresh(facture)
        return facture
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ajouter_avoir(numero, fournisseur_id, date_facture, date_echeance, montant, commentaire, utilisateur):
    return ajouter_facture(numero, fournisseur_id, date_facture, date_echeance, montant, commentaire, utilisateur, "Avoir")


def liste_factures():
    session = get_session()
    try:
        return session.query(Facture).options(selectinload(Facture.fournisseur)).order_by(Facture.date_facture.desc()).all()
    finally:
        session.close()


def supprimer_facture(facture_id, utilisateur=None):
    session = get_session()
    try:
        facture = session.get(Facture, facture_id)
        if facture is None:
            return False
        if (facture.montant_paye or 0) > 0 or facture.paiements:
            raise ValueError(f"La pièce {facture.numero} possède déjà des paiements. Elle ne peut pas être supprimée.")
        session.add(Historique(facture_id=facture.id, action="Suppression",
                               details=f"Pièce {facture.numero} supprimée.", utilisateur=_username(utilisateur)))
        session.delete(facture)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def modifier_facture(facture_id, fournisseur_id, numero, date_facture, date_echeance, montant, commentaire, utilisateur, type_piece="Facture"):
    _validate_invoice_dates_and_amount(date_facture, date_echeance, montant)
    type_piece = "Avoir" if _is_avoir(type_piece) else "Facture"
    session = get_session()
    try:
        facture = session.get(Facture, facture_id)
        if facture is None:
            return False
        if facture.paiements and type_piece == "Avoir":
            raise ValueError("Une facture ayant déjà des paiements ne peut pas être transformée en avoir.")
        if facture.paiements and type_piece == "Facture" and montant < (facture.montant_paye or 0):
            raise ValueError(f"Le nouveau montant ({montant:.2f} DA) ne peut pas être inférieur au montant déjà payé ({facture.montant_paye:.2f} DA).")
        duplicate = session.query(Facture).filter(Facture.numero == numero, Facture.id != facture_id).first()
        if duplicate:
            raise ValueError("Numéro de facture déjà utilisé.")
        facture.numero, facture.fournisseur_id = numero, fournisseur_id
        facture.date_facture, facture.date_echeance = date_facture, date_echeance
        facture.commentaire, facture.type_piece = commentaire, type_piece
        facture.montant = -abs(float(montant)) if type_piece == "Avoir" else abs(float(montant))
        if type_piece == "Avoir":
            facture.montant_paye = 0
        _recalculer_statut(facture)
        session.add(Historique(facture_id=facture.id, action="Modification",
                               details=f"{type_piece} {numero} modifiée", utilisateur=_username(utilisateur)))
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _available_avoirs(session, fournisseur_id):
    """Retourne les avoirs encore disponibles, avec leur crédit restant."""
    avoirs = session.query(Facture).filter(
        Facture.fournisseur_id == fournisseur_id,
        Facture.type_piece == "Avoir",
        Facture.reste < 0,
    ).order_by(Facture.date_facture.asc(), Facture.id.asc()).all()
    return avoirs


def _imputer_avoirs(session, factures, utilisateur):
    """Impute automatiquement les avoirs du fournisseur sur les factures sélectionnées.

    Le champ `reste` d'un avoir représente son crédit encore disponible.
    L'imputation réduit le reste de la facture sans augmenter `montant_paye`.
    """
    total_impute = 0.0
    details = []
    if not factures:
        return total_impute, details
    fournisseur_ids = {f.fournisseur_id for f in factures}
    if len(fournisseur_ids) != 1:
        raise ValueError("Le règlement groupé doit concerner un seul fournisseur.")
    fournisseur_id = next(iter(fournisseur_ids))
    avoirs = _available_avoirs(session, fournisseur_id)
    for facture in factures:
        if _is_avoir(facture):
            raise ValueError(f"L'avoir {facture.numero} ne peut pas être inclus dans un règlement.")
        reste_facture = float(facture.reste or 0)
        if reste_facture <= 0:
            continue
        for avoir in avoirs:
            credit = abs(float(avoir.reste or 0))
            if credit <= 0:
                continue
            imputation = min(reste_facture, credit)
            if imputation <= 0:
                continue
            facture.reste = max(0.0, reste_facture - imputation)
            reste_facture = float(facture.reste)
            avoir.reste = min(0.0, float(avoir.reste) + imputation)
            if facture.reste == 0:
                facture.statut = StatutFacture.PAYEE
            elif facture.montant_paye > 0:
                facture.statut = StatutFacture.PARTIELLE
            else:
                facture.statut = StatutFacture.IMPAYEE
            session.add(Historique(facture_id=facture.id, action="Imputation avoir",
                                   details=f"Avoir {avoir.numero} imputé pour {imputation:.2f} DA sur la facture {facture.numero}.",
                                   utilisateur=_username(utilisateur)))
            session.add(Historique(facture_id=avoir.id, action="Imputation avoir",
                                   details=f"{imputation:.2f} DA imputés sur la facture {facture.numero}.",
                                   utilisateur=_username(utilisateur)))
            total_impute += imputation
            details.append({"avoir": avoir.numero, "facture": facture.numero, "montant": imputation})
            if reste_facture <= 0:
                break
    return total_impute, details


def ajouter_paiement(facture_id, montant, mode, reference, utilisateur):
    _validate_payment_metadata(mode, reference)
    session = get_session()
    try:
        facture = session.get(Facture, facture_id)
        if facture is None:
            raise ValueError("Facture introuvable.")
        if _is_avoir(facture):
            raise ValueError("Un avoir diminue la dette fournisseur et ne peut pas recevoir de paiement.")
        reste = float(facture.reste or 0)
        montant = float(montant)
        if montant <= 0:
            raise ValueError("Le montant du paiement doit être supérieur à zéro.")
        if reste <= 0:
            raise ValueError("Cette facture est déjà entièrement réglée.")
        if montant > reste:
            raise ValueError("Le paiement dépasse le reste à payer.")
        paiement = Paiement(facture_id=facture.id, montant=montant, date_paiement=date.today(),
                            mode_paiement=str(mode).strip(), reference=(str(reference).strip() if reference else None),
                            utilisateur_id=_user_id(utilisateur))
        facture.montant_paye += montant
        _recalculer_statut(facture)
        session.add(paiement)
        session.add(Historique(facture_id=facture.id, action="Paiement",
                               details=f"Paiement de {montant:.2f} DA", utilisateur=_username(utilisateur)))
        session.commit()
        return paiement
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def regler_plusieurs_factures(facture_ids, mode, reference, utilisateur):
    _validate_payment_metadata(mode, reference)
    ids = list(dict.fromkeys(facture_ids or []))
    if not ids:
        raise ValueError("Sélectionnez au moins une facture.")
    session = get_session()
    try:
        factures = session.query(Facture).filter(Facture.id.in_(ids)).order_by(Facture.id.asc()).with_for_update().all()
        if len(factures) != len(ids):
            raise ValueError("Une ou plusieurs factures sélectionnées sont introuvables.")
        if any(_is_avoir(f) for f in factures):
            raise ValueError("Un avoir ne peut pas être inclus dans un règlement.")
        if len({f.fournisseur_id for f in factures}) != 1:
            raise ValueError("Le règlement groupé doit concerner un seul fournisseur.")
        if any(float(f.reste or 0) <= 0 for f in factures):
            raise ValueError("Toutes les factures sélectionnées doivent avoir un reste à payer.")

        total_avant_avoir = sum(float(f.reste or 0) for f in factures)
        total_impute, imputation_details = _imputer_avoirs(session, factures, utilisateur)
        paiements, total = [], 0.0
        for facture in factures:
            reste = float(facture.reste or 0)
            if reste <= 0:
                continue
            paiement = Paiement(facture_id=facture.id, montant=reste, date_paiement=date.today(),
                                mode_paiement=str(mode).strip(), reference=(str(reference).strip() if reference else None),
                                utilisateur_id=_user_id(utilisateur))
            facture.montant_paye += reste
            _recalculer_statut(facture)
            session.add(paiement)
            session.add(Historique(facture_id=facture.id, action="Paiement groupé",
                                   details=f"Facture {facture.numero} réglée en espèces après imputation : {reste:.2f} DA",
                                   utilisateur=_username(utilisateur)))
            paiements.append(paiement)
            total += reste
        session.commit()
        return {
            "factures": len(factures), "paiements": paiements, "total": total,
            "total_avant_avoir": total_avant_avoir, "avoir_impute": total_impute,
            "imputations": imputation_details,
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def liste_paiements(facture_id):
    session = get_session()
    try:
        return session.query(Paiement).filter_by(facture_id=facture_id).order_by(Paiement.date_paiement.desc()).all()
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
