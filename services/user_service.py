import bcrypt
from datetime import datetime

from database.db import get_session
from database.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_admin():
    session = get_session()
    try:
        admin = session.query(User).filter_by(username="admin").first()
        if admin:
            return
        admin = User(username="admin", password=hash_password("admin123"), role="ADMIN")
        session.add(admin)
        session.commit()
    finally:
        session.close()


def login(username, password):
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username, is_active=True).first()
        if not user or not verify_password(password, user.password):
            return None
        user.last_login = datetime.now()
        session.commit()
        session.refresh(user)
        session.expunge(user)
        return user
    finally:
        session.close()


def create_user(username, password, role):
    username = username.strip()
    if not username:
        raise ValueError("Le nom d'utilisateur est obligatoire.")
    if not password:
        raise ValueError("Le mot de passe est obligatoire.")

    session = get_session()
    try:
        existe = session.query(User).filter_by(username=username).first()
        if existe:
            raise ValueError("Utilisateur déjà existant.")
        user = User(username=username, password=hash_password(password), role=role, is_active=True)
        session.add(user)
        session.commit()
    finally:
        session.close()


def get_users():
    session = get_session()
    try:
        users = session.query(User).order_by(User.username.asc()).all()
        for user in users:
            session.expunge(user)
        return users
    finally:
        session.close()


def update_user(user_id, username=None, role=None, password=None):
    session = get_session()
    try:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Utilisateur introuvable.")
        if username:
            duplicate = session.query(User).filter(User.username == username, User.id != user_id).first()
            if duplicate:
                raise ValueError("Ce nom d'utilisateur est déjà utilisé.")
            user.username = username.strip()
        if role:
            user.role = role
        if password:
            user.password = hash_password(password)
        session.commit()
    finally:
        session.close()


def delete_user(user_id):
    session = get_session()
    try:
        user = session.get(User, user_id)
        if user:
            if user.username == "admin":
                raise ValueError("Le compte administrateur principal ne peut pas être supprimé.")
            session.delete(user)
            session.commit()
    finally:
        session.close()


def disable_user(user_id):
    session = get_session()
    try:
        user = session.get(User, user_id)
        if user:
            if user.username == "admin":
                raise ValueError("Le compte administrateur principal ne peut pas être désactivé.")
            user.is_active = False
            session.commit()
    finally:
        session.close()


def enable_user(user_id):
    session = get_session()
    try:
        user = session.get(User, user_id)
        if user:
            user.is_active = True
            session.commit()
    finally:
        session.close()
