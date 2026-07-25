from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
from dataclasses import dataclass

import bcrypt
from sqlalchemy import func, or_, select

from database.connection import session_scope
from database.models import (
    AccessAudit,
    PasswordResetToken,
    User,
    UserStatus,
    utc_now,
)


USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]{3,40}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthError(ValueError):
    pass


class PasswordPolicyError(AuthError):
    pass


@dataclass(frozen=True)
class LoginResult:
    ok: bool
    message: str
    user: User | None = None


def normalize_username(username: str) -> str:
    return username.strip().lower()


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_username(username: str) -> str:
    normalized = normalize_username(username)
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise AuthError(
            "O usuário deve ter de 3 a 40 caracteres e usar apenas letras "
            "minúsculas, números, ponto, hífen ou sublinhado."
        )
    return normalized


def validate_email(email: str) -> str:
    normalized = normalize_email(email)
    if not EMAIL_PATTERN.fullmatch(normalized) or len(normalized) > 254:
        raise AuthError("Informe um e-mail válido.")
    return normalized


def validate_password(password: str) -> None:
    if len(password) < 10:
        raise PasswordPolicyError("A senha deve ter pelo menos 10 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise PasswordPolicyError("Inclua pelo menos uma letra maiúscula.")
    if not re.search(r"[a-z]", password):
        raise PasswordPolicyError("Inclua pelo menos uma letra minúscula.")
    if not re.search(r"\d", password):
        raise PasswordPolicyError("Inclua pelo menos um número.")


def hash_password(password: str) -> str:
    validate_password(password)
    salt = os.urandom(16)
    work_factor = 2**14
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=work_factor,
        r=8,
        p=1,
        dklen=64,
    )
    return "$".join(
        [
            "scrypt",
            str(work_factor),
            "8",
            "1",
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        ]
    )


def verify_password(password: str, encoded: str) -> bool:
    if encoded.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                encoded.encode("utf-8"),
            )
        except (ValueError, TypeError):
            return False

    try:
        algorithm, n_value, r_value, p_value, salt_b64, digest_b64 = encoded.split(
            "$",
            5,
        )
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n_value),
            r=int(r_value),
            p=int(p_value),
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def authenticate(identifier: str, password: str) -> LoginResult:
    normalized = identifier.strip().lower()
    if not normalized or not password:
        return LoginResult(False, "Informe usuário ou e-mail e senha.")

    with session_scope() as session:
        user = session.scalar(
            select(User).where(
                or_(
                    func.lower(User.username) == normalized,
                    func.lower(User.email) == normalized,
                )
            )
        )

        if user is None or not verify_password(password, user.password_hash):
            return LoginResult(False, "Usuário/e-mail ou senha inválidos.")

        if user.status == UserStatus.PENDING.value:
            return LoginResult(
                False,
                "Seu cadastro ainda está aguardando aprovação.",
            )
        if user.status == UserStatus.REJECTED.value:
            return LoginResult(
                False,
                "Esta solicitação de cadastro não foi aprovada.",
            )
        if user.status == UserStatus.BLOCKED.value:
            return LoginResult(
                False,
                "Este acesso está bloqueado. Procure o administrador.",
            )
        if user.status != UserStatus.APPROVED.value:
            return LoginResult(False, "Este acesso não está disponível.")

        user.last_login_at = utc_now()
        session.add(
            AccessAudit(
                actor_user_id=user.id,
                target_user_id=user.id,
                action="login_success",
            )
        )
        session.flush()
        session.expunge(user)
        return LoginResult(True, "Acesso realizado com sucesso.", user)


def _clean_legacy_hash(value: str) -> str:
    cleaned = value.strip()
    if (
        len(cleaned) >= 2
        and cleaned[0] == cleaned[-1]
        and cleaned[0] in {"'", '"'}
    ):
        cleaned = cleaned[1:-1]
    return cleaned


def _legacy_credentials() -> tuple[tuple[str, str, bool], ...]:
    return tuple(
        (username.strip().lower(), _clean_legacy_hash(encoded), is_admin)
        for username, encoded, is_admin in (
            (
                os.getenv("LEGACY_ADMIN_USERNAME", ""),
                os.getenv("LEGACY_ADMIN_PASSWORD_HASH", ""),
                True,
            ),
            (
                os.getenv("LEGACY_CLIENT_USERNAME", ""),
                os.getenv("LEGACY_CLIENT_PASSWORD_HASH", ""),
                False,
            ),
        )
        if username.strip() and encoded.strip()
    )


def authenticate_legacy(identifier: str, password: str) -> LoginResult | None:
    """
    Migra uma credencial bcrypt da camada HTTP antiga para a base da LEX.

    A migração acontece uma única vez por usuário. Depois de uma troca de senha
    na LEX, o hash legado não pode voltar a ser aceito.
    """
    normalized = normalize_username(identifier)
    credential = next(
        (
            item
            for item in _legacy_credentials()
            if hmac.compare_digest(item[0], normalized)
        ),
        None,
    )
    if credential is None or not password:
        return None

    legacy_username, legacy_hash, legacy_is_admin = credential
    try:
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            legacy_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        password_matches = False
    if not password_matches:
        return None

    with session_scope() as session:
        user = session.scalar(
            select(User).where(func.lower(User.username) == legacy_username)
        )

        if user is not None:
            already_migrated = session.scalar(
                select(AccessAudit.id).where(
                    AccessAudit.target_user_id == user.id,
                    AccessAudit.action == "legacy_access_migrated",
                )
            )
            if already_migrated is not None:
                return None
            if user.status == UserStatus.PENDING.value:
                return LoginResult(
                    False,
                    "Seu cadastro ainda está aguardando aprovação.",
                )
            if user.status == UserStatus.REJECTED.value:
                return LoginResult(
                    False,
                    "Esta solicitação de cadastro não foi aprovada.",
                )
            if user.status == UserStatus.BLOCKED.value:
                return LoginResult(
                    False,
                    "Este acesso está bloqueado. Procure o administrador.",
                )
            if user.status != UserStatus.APPROVED.value:
                return LoginResult(False, "Este acesso não está disponível.")
        else:
            user = User(
                username=legacy_username,
                email=f"{legacy_username}@legacy.local",
                full_name=(
                    "DMT Administrador"
                    if legacy_is_admin
                    else legacy_username.replace("-", " ").title()
                ),
                password_hash=legacy_hash,
                status=UserStatus.APPROVED.value,
                is_admin=legacy_is_admin,
                approved_at=utc_now(),
            )
            session.add(user)
            session.flush()

        user.password_hash = legacy_hash
        user.password_changed_at = utc_now()
        session.add(
            AccessAudit(
                actor_user_id=user.id,
                target_user_id=user.id,
                action="legacy_access_migrated",
            )
        )

    return authenticate(legacy_username, password)


def change_password(user_id: int, current_password: str, new_password: str) -> None:
    validate_password(new_password)

    with session_scope() as session:
        user = session.get(User, user_id)
        if user is None:
            raise AuthError("Usuário não encontrado.")
        if not verify_password(current_password, user.password_hash):
            raise AuthError("A senha atual não confere.")
        if verify_password(new_password, user.password_hash):
            raise AuthError("A nova senha deve ser diferente da senha atual.")

        user.password_hash = hash_password(new_password)
        user.password_changed_at = utc_now()
        for reset_token in session.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
        ):
            reset_token.used_at = user.password_changed_at
        session.add(
            AccessAudit(
                actor_user_id=user.id,
                target_user_id=user.id,
                action="password_changed_by_user",
            )
        )
