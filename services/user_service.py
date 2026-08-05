import bcrypt
from datetime import datetime

from database.db import get_session
from database.models import User


# =====================================================
# HASH
# =====================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )


# =====================================================
# ADMIN
# =====================================================

def create_admin():

    session = get_session()

    admin = session.query(User).filter_by(username="admin").first()

    if admin:
        session.close()
        return

    admin = User(
        username="admin",
        password=hash_password("admin123"),
        role="ADMIN"
    )

    session.add(admin)
    session.commit()
    session.close()


# =====================================================
# LOGIN
# =====================================================

def login(username, password):

    session = get_session()

    user = session.query(User).filter_by(
        username=username,
        is_active=True
    ).first()

    if not user:
        session.close()
        return None

    if not verify_password(password, user.password):
        session.close()
        return None

    user.last_login = datetime.now()

    session.commit()

    session.refresh(user)

    session.expunge(user)

    session.close()

    return user


# =====================================================
# CREATE USER
# =====================================================

def create_user(username, password, role):

    session = get_session()

    existe = session.query(User).filter_by(
        username=username
    ).first()

    if existe:
        session.close()
        raise Exception("Utilisateur déjà existant.")

    user = User(
        username=username,
        password=hash_password(password),
        role=role
    )

    session.add(user)

    session.commit()

    session.close()


# =====================================================
# LIST USERS
# =====================================================

def get_users():

    session = get_session()

    users = session.query(User).all()

    session.close()

    return users


# =====================================================
# DELETE USER
# =====================================================

def delete_user(user_id):

    session = get_session()

    user = session.get(User, user_id)

    if user:

        session.delete(user)

        session.commit()

    session.close()


# =====================================================
# DISABLE USER
# =====================================================

def disable_user(user_id):

    session = get_session()

    user = session.get(User, user_id)

    if user:

        user.is_active = False

        session.commit()

    session.close()