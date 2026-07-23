from __future__ import annotations

import streamlit as st

from services.access_control_service import reset_password_with_token
from services.auth_service import AuthError, authenticate
from services.user_service import RegistrationData, register_user
from utils.session import current_user, prepare_application, sign_in, sign_out


def _render_reset_form(token: str) -> None:
    st.subheader("Defina uma nova senha")
    st.caption(
        "O link é temporário e deixa de funcionar depois da primeira utilização."
    )
    with st.form("password_reset_form"):
        password = st.text_input("Nova senha", type="password")
        confirmation = st.text_input("Confirme a nova senha", type="password")
        submitted = st.form_submit_button(
            "Salvar nova senha",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if password != confirmation:
            st.error("As senhas não coincidem.")
            return
        try:
            reset_password_with_token(token, password)
        except AuthError as exc:
            st.error(str(exc))
            return

        st.query_params.clear()
        st.success("Senha alterada. Você já pode entrar com a nova senha.")


def _render_login_form(form_key: str) -> None:
    with st.form(form_key):
        identifier = st.text_input(
            "Usuário ou e-mail",
            placeholder="seu.usuario ou voce@exemplo.com",
        )
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button(
            "Entrar",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        result = authenticate(identifier, password)
        if not result.ok or result.user is None:
            st.error(result.message)
            return
        sign_in(result.user)
        st.success(f"Bem-vindo(a), {result.user.full_name}.")
        st.rerun()


def _render_registration_form(form_key: str) -> None:
    st.caption(
        "Pedimos somente os dados necessários para identificar e administrar "
        "o acesso. A aprovação é feita pelo administrador."
    )
    with st.form(form_key):
        full_name = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        username = st.text_input(
            "Nome de usuário",
            help="Use letras minúsculas, números, ponto, hífen ou sublinhado.",
        )
        professional_role = st.selectbox(
            "Perfil profissional",
            (
                "Advogado(a)",
                "Contador(a)",
                "Consultor(a)",
                "Empresário(a)",
                "Estudante",
                "Outro",
            ),
        )
        legal_area = st.text_input(
            "Área de interesse (opcional)",
            placeholder="Ex.: Direito Tributário",
        )
        password = st.text_input(
            "Crie uma senha",
            type="password",
            help=(
                "Mínimo de 10 caracteres, com letra maiúscula, minúscula e número."
            ),
        )
        confirmation = st.text_input("Confirme a senha", type="password")
        accepted = st.checkbox(
            "Li e compreendo que o cadastro depende de aprovação."
        )
        submitted = st.form_submit_button(
            "Solicitar cadastro",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not accepted:
            st.error("Confirme que compreende o fluxo de aprovação.")
            return
        if password != confirmation:
            st.error("As senhas não coincidem.")
            return

        try:
            register_user(
                RegistrationData(
                    username=username,
                    email=email,
                    full_name=full_name,
                    password=password,
                    professional_role=professional_role,
                    legal_area=legal_area,
                )
            )
        except AuthError as exc:
            st.error(str(exc))
            return

        st.success(
            "Cadastro enviado. Você poderá entrar depois que o administrador "
            "aprovar a solicitação; a confirmação será enviada por e-mail."
        )


def render_access_portal(*, compact: bool = False) -> None:
    prepare_application()
    token = str(st.query_params.get("reset_token", "")).strip()
    if token:
        _render_reset_form(token)
        return

    user = current_user()
    if user is not None:
        left, right = st.columns([4, 1])
        with left:
            st.success(f"Você está conectado(a) como {user.full_name}.")
        with right:
            if st.button("Sair", key=f"logout_{'compact' if compact else 'page'}"):
                sign_out()
                st.rerun()
        return

    if compact:
        st.markdown("### Acesse a plataforma")
    login_tab, register_tab = st.tabs(["Entrar", "Solicitar cadastro"])
    with login_tab:
        _render_login_form(f"login_form_{'compact' if compact else 'page'}")
    with register_tab:
        _render_registration_form(
            f"registration_form_{'compact' if compact else 'page'}"
        )
