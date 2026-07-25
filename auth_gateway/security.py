from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlsplit


SESSION_VERSION = 1


@dataclass(frozen=True)
class SessionIdentity:
    user_id: int
    issued_at: int
    expires_at: int
    password_changed_at: int | None


def _encode_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode_bytes(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))


def _datetime_timestamp(value: datetime | None) -> int | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(value.timestamp())


def create_session_token(
    *,
    user_id: int,
    secret: str,
    password_changed_at: datetime | None = None,
    now: int | None = None,
    lifetime_seconds: int = 43_200,
) -> str:
    issued_at = int(time.time() if now is None else now)
    payload = {
        "exp": issued_at + lifetime_seconds,
        "iat": issued_at,
        "nonce": secrets.token_urlsafe(12),
        "pwd": _datetime_timestamp(password_changed_at),
        "uid": int(user_id),
        "v": SESSION_VERSION,
    }
    encoded_payload = _encode_bytes(
        json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_encode_bytes(signature)}"


def decode_session_token(
    token: str,
    *,
    secret: str,
    now: int | None = None,
) -> SessionIdentity | None:
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        supplied_signature = _decode_bytes(encoded_signature)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            return None

        payload = json.loads(_decode_bytes(encoded_payload).decode("utf-8"))
        current_time = int(time.time() if now is None else now)
        if payload.get("v") != SESSION_VERSION:
            return None
        if int(payload["iat"]) > current_time + 60:
            return None
        if int(payload["exp"]) <= current_time:
            return None
        if int(payload["uid"]) <= 0:
            return None

        password_changed_at = payload.get("pwd")
        return SessionIdentity(
            user_id=int(payload["uid"]),
            issued_at=int(payload["iat"]),
            expires_at=int(payload["exp"]),
            password_changed_at=(
                int(password_changed_at)
                if password_changed_at is not None
                else None
            ),
        )
    except (
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError,
        binascii.Error,
        UnicodeDecodeError,
    ):
        return None


def session_matches_password_state(
    identity: SessionIdentity,
    password_changed_at: datetime | None,
) -> bool:
    return identity.password_changed_at == _datetime_timestamp(password_changed_at)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_matches(cookie_value: str | None, form_value: str | None) -> bool:
    if not cookie_value or not form_value:
        return False
    return hmac.compare_digest(cookie_value, form_value)


def safe_redirect_url(
    candidate: str | None,
    *,
    allowed_hosts: set[str],
    default_url: str,
) -> str:
    if not candidate:
        return default_url

    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return default_url

    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        return default_url
    if parsed.username or parsed.password:
        return default_url
    return candidate
