from __future__ import annotations

import os
from urllib.parse import quote

import streamlit as st

from database.connection import init_database
from database.models import User, UserStatus
from services.user_service import bootstrap_admin_from_env, get_user


SESSION_USER_ID = "lex_authenticated_user_id"
AUTH_USER_ID_HEADER = "X-Auth-User-Id"


def prepare_application() -> None:
    init_database()
    bootstrap_admin_from_env()


def sign_in(user: User) -> None:
    st.session_state[SESSION_USER_ID] = user.id


def sign_out() -> None:
    st.session_state.pop(SESSION_USER_ID, None)


def _gateway_user_id() -> int | None:
    try:
        raw_user_id = st.context.headers.get(AUTH_USER_ID_HEADER)
    except (AttributeError, RuntimeError):
        return None
    if not raw_user_id:
        return None
    try:
        return int(raw_user_id)
    except (TypeError, ValueError):
        return None


def current_request_url() -> str:
    try:
        return str(st.context.url)
    except (AttributeError, RuntimeError):
        return os.getenv(
            "LEX_PUBLIC_URL",
            "https://lex.54-94-43-149.sslip.io",
        )


def auth_url(path: str = "/login", *, next_url: str | None = None) -> str:
    base_url = os.getenv(
        "AUTH_PUBLIC_URL",
        "https://acesso.54-94-43-149.sslip.io",
    ).rstrip("/")
    target = next_url or current_request_url()
    return f"{base_url}{path}?next={quote(target, safe='')}"


def logout_url(*, next_url: str | None = None) -> str:
    return auth_url("/logout", next_url=next_url)


def current_user() -> User | None:
    raw_user_id = _gateway_user_id()
    if raw_user_id is None:
        raw_user_id = st.session_state.get(SESSION_USER_ID)
    if raw_user_id is None:
        return None

    user = get_user(int(raw_user_id))
    if user is None or user.status != UserStatus.APPROVED.value:
        sign_out()
        return None
    return user


def require_user(*, admin: bool = False) -> User:
    user = current_user()
    if user is None:
        st.warning("Entre com uma conta aprovada para acessar esta página.")
        st.link_button(
            "🔑 Entrar ou solicitar cadastro",
            auth_url(),
            use_container_width=True,
        )
        st.stop()

    if admin and not user.is_admin:
        st.error("Esta área é restrita ao administrador.")
        st.stop()
    return user
