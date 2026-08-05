from database.db import get_session
from database.models import Fournisseur


# ==========================
# AJOUTER
# ==========================

def ajouter_fournisseur(
    nom,
    contact="",
    telephone="",
    email="",
    adresse="",
    ville=""
):

    session = get_session()

    fournisseur = Fournisseur(
        nom=nom,
        contact=contact,
        telephone=telephone,
        email=email,
        adresse=adresse,
        ville=ville
    )

    session.add(fournisseur)
    session.commit()
    session.refresh(fournisseur)
    session.close()

    return fournisseur


# ==========================
# LISTE
# ==========================

def liste_fournisseurs():

    session = get_session()

    fournisseurs = (
        session.query(Fournisseur)
        .order_by(Fournisseur.nom)
        .all()
    )

    session.close()

    return fournisseurs


# ==========================
# RECHERCHE
# ==========================

def rechercher_fournisseur(mot):

    session = get_session()

    fournisseurs = (
        session.query(Fournisseur)
        .filter(Fournisseur.nom.ilike(f"%{mot}%"))
        .all()
    )

    session.close()

    return fournisseurs


# ==========================
# MODIFIER
# ==========================

def modifier_fournisseur(
    fournisseur_id,
    nom,
    contact,
    telephone,
    email,
    adresse,
    ville
):

    session = get_session()

    fournisseur = session.get(Fournisseur, fournisseur_id)

    if not fournisseur:
        session.close()
        return False

    fournisseur.nom = nom
    fournisseur.contact = contact
    fournisseur.telephone = telephone
    fournisseur.email = email
    fournisseur.adresse = adresse
    fournisseur.ville = ville

    session.commit()
    session.close()

    return True


# ==========================
# SUPPRIMER
# ==========================

def supprimer_fournisseur(fournisseur_id):

    session = get_session()

    fournisseur = session.get(Fournisseur, fournisseur_id)

    if fournisseur:
        session.delete(fournisseur)
        session.commit()

    session.close()


# ==========================
# DETAILS
# ==========================

def get_fournisseur(fournisseur_id):

    session = get_session()

    fournisseur = session.get(Fournisseur, fournisseur_id)

    session.close()

    return fournisseur