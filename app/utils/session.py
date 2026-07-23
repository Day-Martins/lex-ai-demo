from __future__ import annotations

import streamlit as st

from database.connection import init_database
from database.models import User, UserStatus
from services.user_service import bootstrap_admin_from_env, get_user


SESSION_USER_ID = "lex_authenticated_user_id"


def prepare_application() -> None:
    init_database()
    bootstrap_admin_from_env()


def sign_in(user: User) -> None:
    st.session_state[SESSION_USER_ID] = user.id


def sign_out() -> None:
    st.session_state.pop(SESSION_USER_ID, None)


def current_user() -> User | None:
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
        st.markdown("[🔑 Entrar ou solicitar cadastro](/Acesso)")
        st.stop()

    if admin and not user.is_admin:
        st.error("Esta área é restrita ao administrador.")
        st.stop()
    return user
