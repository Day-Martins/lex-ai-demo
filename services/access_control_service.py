from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select

from database.connection import session_scope
from database.models import (
    AccessAudit,
    PasswordResetToken,
    User,
    UserStatus,
    utc_now,
)
from services.auth_service import AuthError, hash_password, validate_password
from services.email_service import (
    DeliveryResult,
    send_approval_email,
    send_rejection_email,
    send_reset_email,
)


@dataclass(frozen=True)
class AccessActionResult:
    user: User
    delivery: DeliveryResult | None = None
    reset_token: str | None = None


def _detached_user(session, user: User) -> User:
    session.flush()
    session.expunge(user)
    return user


def _require_admin(session, actor_user_id: int) -> User:
    actor = session.get(User, actor_user_id)
    if (
        actor is None
        or not actor.is_admin
        or actor.status != UserStatus.APPROVED.value
    ):
        raise AuthError("Ação permitida somente para administrador ativo.")
    return actor


def approve_user(
    actor_user_id: int,
    target_user_id: int,
    *,
    notify: bool = True,
) -> AccessActionResult:
    with session_scope() as session:
        _require_admin(session, actor_user_id)
        target = session.get(User, target_user_id)
        if target is None:
            raise AuthError("Usuário não encontrado.")
        if target.is_admin:
            raise AuthError("A conta administrativa não pode ser alterada aqui.")

        target.status = UserStatus.APPROVED.value
        target.approved_at = utc_now()
        target.approved_by_id = actor_user_id
        target.blocked_at = None
        session.add(
            AccessAudit(
                actor_user_id=actor_user_id,
                target_user_id=target.id,
                action="access_approved",
            )
        )
        email = target.email
        full_name = target.full_name
        detached = _detached_user(session, target)

    delivery = send_approval_email(email, full_name) if notify else None
    return AccessActionResult(detached, delivery)


def reject_user(
    actor_user_id: int,
    target_user_id: int,
    *,
    notify: bool = True,
) -> AccessActionResult:
    with session_scope() as session:
        _require_admin(session, actor_user_id)
        target = session.get(User, target_user_id)
        if target is None:
            raise AuthError("Usuário não encontrado.")
        if target.is_admin:
            raise AuthError("A conta administrativa não pode ser alterada aqui.")

        target.status = UserStatus.REJECTED.value
        target.approved_at = None
        target.approved_by_id = actor_user_id
        target.blocked_at = None
        session.add(
            AccessAudit(
                actor_user_id=actor_user_id,
                target_user_id=target.id,
                action="access_rejected",
            )
        )
        email = target.email
        full_name = target.full_name
        detached = _detached_user(session, target)

    delivery = send_rejection_email(email, full_name) if notify else None
    return AccessActionResult(detached, delivery)


def block_user(actor_user_id: int, target_user_id: int) -> AccessActionResult:
    with session_scope() as session:
        _require_admin(session, actor_user_id)
        target = session.get(User, target_user_id)
        if target is None:
            raise AuthError("Usuário não encontrado.")
        if target.is_admin:
            raise AuthError("A conta administrativa não pode ser bloqueada.")

        target.status = UserStatus.BLOCKED.value
        target.blocked_at = utc_now()
        session.add(
            AccessAudit(
                actor_user_id=actor_user_id,
                target_user_id=target.id,
                action="access_blocked",
            )
        )
        return AccessActionResult(_detached_user(session, target))


def reactivate_user(actor_user_id: int, target_user_id: int) -> AccessActionResult:
    with session_scope() as session:
        _require_admin(session, actor_user_id)
        target = session.get(User, target_user_id)
        if target is None:
            raise AuthError("Usuário não encontrado.")
        if target.is_admin:
            raise AuthError("A conta administrativa não pode ser alterada aqui.")

        target.status = UserStatus.APPROVED.value
        target.blocked_at = None
        if target.approved_at is None:
            target.approved_at = utc_now()
        target.approved_by_id = actor_user_id
        session.add(
            AccessAudit(
                actor_user_id=actor_user_id,
                target_user_id=target.id,
                action="access_reactivated",
            )
        )
        return AccessActionResult(_detached_user(session, target))


def request_password_reset(
    actor_user_id: int,
    target_user_id: int,
    *,
    notify: bool = True,
    validity_minutes: int = 60,
) -> AccessActionResult:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    with session_scope() as session:
        _require_admin(session, actor_user_id)
        target = session.get(User, target_user_id)
        if target is None:
            raise AuthError("Usuário não encontrado.")
        if target.status not in {
            UserStatus.APPROVED.value,
            UserStatus.BLOCKED.value,
        }:
            raise AuthError("A redefinição exige um cadastro aprovado.")

        now = utc_now()
        for previous_token in session.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == target.id,
                PasswordResetToken.used_at.is_(None),
            )
        ):
            previous_token.used_at = now

        session.add(
            PasswordResetToken(
                user_id=target.id,
                token_hash=token_hash,
                expires_at=now + timedelta(minutes=validity_minutes),
                requested_by_admin_id=actor_user_id,
            )
        )
        session.add(
            AccessAudit(
                actor_user_id=actor_user_id,
                target_user_id=target.id,
                action="password_reset_requested",
            )
        )
        email = target.email
        full_name = target.full_name
        detached = _detached_user(session, target)

    delivery = (
        send_reset_email(email, full_name, raw_token)
        if notify
        else None
    )
    return AccessActionResult(detached, delivery, raw_token)


def reset_password_with_token(raw_token: str, new_password: str) -> User:
    validate_password(new_password)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    now = utc_now()

    with session_scope() as session:
        reset_token = session.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
            )
        )
        if reset_token is None:
            raise AuthError("Este link de redefinição é inválido ou já foi usado.")

        expires_at = reset_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=now.tzinfo)
        if expires_at < now:
            raise AuthError("Este link de redefinição expirou.")

        user = session.get(User, reset_token.user_id)
        if user is None:
            raise AuthError("Usuário não encontrado.")

        user.password_hash = hash_password(new_password)
        user.password_changed_at = now
        for token in session.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
        ):
            token.used_at = now
        session.add(
            AccessAudit(
                actor_user_id=user.id,
                target_user_id=user.id,
                action="password_reset_completed",
            )
        )
        return _detached_user(session, user)
