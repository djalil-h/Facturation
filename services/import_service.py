from datetime import date, datetime, timedelta
from pathlib import Path
import re
import unicodedata

from openpyxl import load_workbook

from database.db import get_session
from database.models import Facture, Fournisseur, Paiement, Historique, JournalAction, StatutFacture

ALIASES = {
    "numero": {"numero", "n° facture", "no facture", "n facture", "facture", "reference facture", "ref facture"},
    "fournisseur": {"fournisseur", "nom fournisseur", "supplier", "vendor"},
    "date_facture": {"date facture", "date_facturation", "date", "date emission", "date d emission"},
    "date_echeance": {"date echeance", "echeance", "date paiement limite", "date limite"},
    "montant": {"montant", "total", "montant total", "ttc", "total ttc"},
    "montant_paye": {"montant paye", "paye", "deja paye", "total paye", "regle"},
    "date_paiement": {"date paiement", "date du paiement"},
    "mode_paiement": {"mode paiement", "mode", "moyen paiement"},
    "reference_paiement": {"reference paiement", "ref paiement", "reference reglement"},
    "commentaire": {"commentaire", "note", "notes", "observation", "observations"},
}


def _normalize(value):
    text = "" if value is None else str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text)


def _parse_date(value, field):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        return (datetime(1899, 12, 30) + timedelta(days=float(value))).date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"{field}: date invalide « {value} »")


def _parse_amount(value, field):
    if value in (None, ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("DA", "").replace("da", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".") if text.rfind(",") > text.rfind(".") else text.replace(",", "")
    else:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"{field}: montant invalide « {value} »") from exc


def _header_map(headers):
    normalized = {_normalize(h): i for i, h in enumerate(headers) if h not in (None, "")}
    result = {}
    for field, aliases in ALIASES.items():
        for alias in aliases:
            if _normalize(alias) in normalized:
                result[field] = normalized[_normalize(alias)]
                break
    return result


def _cell(row, mapping, field, default=None):
    index = mapping.get(field)
    return default if index is None or index >= len(row) else row[index]


def importer_factures_excel(filepath, utilisateur=None, creer_fournisseurs=True):
    """Importe des factures historiques depuis un .xlsx.

    Obligatoire : Numero, Fournisseur, Date facture, Montant.
    Optionnel : Date échéance, Montant payé, Date paiement,
    Mode paiement, Référence paiement, Commentaire.
    """
    path = Path(filepath)
    if path.suffix.lower() != ".xlsx":
        raise ValueError("Le fichier doit être au format Excel .xlsx")

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(workbook.active.iter_rows(values_only=True))
        if not rows:
            raise ValueError("Le fichier Excel est vide.")

        mapping = _header_map(rows[0])
        required = ["numero", "fournisseur", "date_facture", "montant"]
        missing = [field for field in required if field not in mapping]
        if missing:
            raise ValueError("Colonnes obligatoires absentes : " + ", ".join(missing))

        session = get_session()
        imported = skipped = suppliers_created = payments_created = 0
        errors = []
        try:
            supplier_cache = {_normalize(f.nom): f for f in session.query(Fournisseur).all()}
            existing_numbers = {n for (n,) in session.query(Facture.numero).all()}
            user_id = getattr(utilisateur, "id", None)
            username = getattr(utilisateur, "username", "Invité")

            for excel_row, row in enumerate(rows[1:], start=2):
                if not any(value not in (None, "") for value in row):
                    continue
                try:
                    numero = str(_cell(row, mapping, "numero", "")).strip()
                    supplier_name = str(_cell(row, mapping, "fournisseur", "")).strip()
                    if not numero:
                        raise ValueError("Numéro de facture vide")
                    if not supplier_name:
                        raise ValueError("Fournisseur vide")
                    if numero in existing_numbers:
                        skipped += 1
                        errors.append(f"Ligne {excel_row} : facture {numero} déjà existante (ignorée).")
                        continue

                    date_facture = _parse_date(_cell(row, mapping, "date_facture"), "Date facture")
                    date_echeance = _parse_date(_cell(row, mapping, "date_echeance", date_facture), "Date échéance") or date_facture
                    montant = _parse_amount(_cell(row, mapping, "montant"), "Montant")
                    montant_paye = _parse_amount(_cell(row, mapping, "montant_paye", 0), "Montant payé")
                    if montant < 0 or montant_paye < 0:
                        raise ValueError("Les montants ne peuvent pas être négatifs")
                    if montant_paye > montant:
                        raise ValueError("Le montant payé dépasse le montant de la facture")

                    supplier_key = _normalize(supplier_name)
                    fournisseur = supplier_cache.get(supplier_key)
                    if fournisseur is None:
                        if not creer_fournisseurs:
                            raise ValueError(f"Fournisseur introuvable : {supplier_name}")
                        fournisseur = Fournisseur(nom=supplier_name)
                        session.add(fournisseur)
                        session.flush()
                        supplier_cache[supplier_key] = fournisseur
                        suppliers_created += 1

                    reste = montant - montant_paye
                    statut = StatutFacture.PAYEE if reste == 0 else StatutFacture.PARTIELLE if montant_paye > 0 else StatutFacture.IMPAYEE
                    facture = Facture(
                        numero=numero,
                        fournisseur_id=fournisseur.id,
                        date_facture=date_facture,
                        date_echeance=date_echeance,
                        montant=montant,
                        montant_paye=montant_paye,
                        reste=reste,
                        statut=statut,
                        commentaire=str(_cell(row, mapping, "commentaire", "") or "").strip(),
                        created_by=user_id,
                    )
                    session.add(facture)
                    session.flush()
                    session.add(Historique(facture_id=facture.id, action="Import Excel", details=f"Facture {numero} importée depuis {path.name}", utilisateur=username))

                    if montant_paye > 0:
                        date_paiement = _parse_date(_cell(row, mapping, "date_paiement", date_facture), "Date paiement") or date_facture
                        session.add(Paiement(
                            facture_id=facture.id,
                            montant=montant_paye,
                            date_paiement=date_paiement,
                            mode_paiement=str(_cell(row, mapping, "mode_paiement", "") or "").strip(),
                            reference=str(_cell(row, mapping, "reference_paiement", "") or "").strip(),
                            utilisateur_id=user_id,
                        ))
                        payments_created += 1
                    existing_numbers.add(numero)
                    imported += 1
                except Exception as exc:
                    errors.append(f"Ligne {excel_row} : {exc}")

            session.add(JournalAction(
                action="Import Excel",
                description=f"{imported} facture(s) importée(s) depuis {path.name}, {skipped} doublon(s), {len(errors) - skipped} erreur(s), {suppliers_created} fournisseur(s) créé(s).",
                utilisateur=username,
            ))
            session.commit()
            return {"imported": imported, "skipped": skipped, "errors": errors, "suppliers_created": suppliers_created, "payments_created": payments_created, "filename": path.name}
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    finally:
        workbook.close()
