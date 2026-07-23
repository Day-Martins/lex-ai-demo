from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from database.connection import session_scope
from database.models import AccessAudit, User, UserStatus
from services.auth_service import (
    AuthError,
    hash_password,
    normalize_email,
    validate_email,
    validate_username,
)


@dataclass(frozen=True)
class RegistrationData:
    username: str
    email: str
    full_name: str
    password: str
    professional_role: str | None = None
    legal_area: str | None = None


def _clean_optional(value: str | None, max_length: int) -> str | None:
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return cleaned[:max_length]


def register_user(data: RegistrationData) -> User:
    username = validate_username(data.username)
    email = validate_email(data.email)
    full_name = data.full_name.strip()

    if len(full_name) < 3 or len(full_name) > 120:
        raise AuthError("Informe seu nome completo.")

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        professional_role=_clean_optional(data.professional_role, 80),
        legal_area=_clean_optional(data.legal_area, 100),
        password_hash=hash_password(data.password),
        status=UserStatus.PENDING.value,
        is_admin=False,
    )

    try:
        with session_scope() as session:
            duplicate = session.scalar(
                select(User).where(
                    or_(
                        func.lower(User.username) == username,
                        func.lower(User.email) == email,
                    )
                )
            )
            if duplicate is not None:
                if duplicate.username.lower() == username:
                    raise AuthError("Este nome de usuário já está em uso.")
                raise AuthError("Já existe um cadastro com este e-mail.")

            session.add(user)
            session.flush()
            session.add(
                AccessAudit(
                    target_user_id=user.id,
                    action="registration_requested",
                )
            )
            session.expunge(user)
            return user
    except IntegrityError as exc:
        raise AuthError("Usuário ou e-mail já cadastrado.") from exc


def get_user(user_id: int) -> User | None:
    with session_scope() as session:
        user = session.get(User, user_id)
        if user is not None:
            session.expunge(user)
        return user


def list_users() -> list[User]:
    with session_scope() as session:
        users = list(
            session.scalars(
                select(User).order_by(User.created_at.desc(), User.full_name)
            )
        )
        for user in users:
            session.expunge(user)
        return users


def update_profile(
    user_id: int,
    *,
    full_name: str,
    professional_role: str | None,
    legal_area: str | None,
) -> User:
    cleaned_name = full_name.strip()
    if len(cleaned_name) < 3 or len(cleaned_name) > 120:
        raise AuthError("Informe seu nome completo.")

    with session_scope() as session:
        user = session.get(User, user_id)
        if user is None:
            raise AuthError("Usuário não encontrado.")

        user.full_name = cleaned_name
        user.professional_role = _clean_optional(professional_role, 80)
        user.legal_area = _clean_optional(legal_area, 100)
        session.add(
            AccessAudit(
                actor_user_id=user.id,
                target_user_id=user.id,
                action="profile_updated",
            )
        )
        session.flush()
        session.expunge(user)
        return user


def bootstrap_admin_from_env() -> bool:
    """
    Cria o administrador inicial somente quando a senha segura foi configurada.

    Em bases já existentes, nunca altera a senha ou os dados do administrador.
    """
    username = os.getenv("LEX_ADMIN_USERNAME", "dmt").strip().lower()
    password = os.getenv("LEX_ADMIN_INITIAL_PASSWORD", "")
    email = normalize_email(
        os.getenv("LEX_ADMIN_EMAIL", "dmt@localhost.invalid")
    )
    full_name = os.getenv("LEX_ADMIN_NAME", "DMT Administrador").strip()

    with session_scope() as session:
        existing = session.scalar(
            select(User).where(func.lower(User.username) == username)
        )
        if existing is not None:
            return False

    if not password:
        return False

    validate_username(username)
    validate_email(email)
    password_hash = hash_password(password)

    with session_scope() as session:
        admin = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            status=UserStatus.APPROVED.value,
            is_admin=True,
        )
        session.add(admin)
        session.flush()
        session.add(
            AccessAudit(
                actor_user_id=admin.id,
                target_user_id=admin.id,
                action="bootstrap_admin_created",
            )
        )
    return True
