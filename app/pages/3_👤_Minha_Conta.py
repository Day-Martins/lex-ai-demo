import streamlit as st

from services.auth_service import AuthError, change_password
from services.user_service import update_profile
from utils.footer import render_footer
from utils.page_style import apply_page_style, render_page_heading
from utils.session import prepare_application, require_user, sign_out


st.set_page_config(
    page_title="Minha Conta | LEX AI",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()
prepare_application()
user = require_user()

render_page_heading(
    "Área do usuário",
    "Minha Conta",
    (
        "Atualize os dados profissionais básicos e sua senha. Informações "
        "sensíveis ou desnecessárias não são solicitadas nesta etapa."
    ),
)

profile_tab, password_tab, access_tab = st.tabs(
    ["Dados da conta", "Alterar senha", "Acesso e segurança"]
)

with profile_tab:
    with st.form("profile_form"):
        st.text_input("Nome de usuário", value=user.username, disabled=True)
        st.text_input("E-mail", value=user.email, disabled=True)
        full_name = st.text_input("Nome completo", value=user.full_name)
        professional_role = st.text_input(
            "Perfil profissional",
            value=user.professional_role or "",
        )
        legal_area = st.text_input(
            "Área de interesse",
            value=user.legal_area or "",
        )
        save_profile = st.form_submit_button(
            "Salvar alterações",
            type="primary",
        )

    if save_profile:
        try:
            updated = update_profile(
                user.id,
                full_name=full_name,
                professional_role=professional_role,
                legal_area=legal_area,
            )
            st.success("Dados atualizados.")
            user = updated
        except AuthError as exc:
            st.error(str(exc))

with password_tab:
    st.caption(
        "A nova senha precisa ter pelo menos 10 caracteres, incluindo letra "
        "maiúscula, letra minúscula e número."
    )
    with st.form("change_password_form"):
        current_password = st.text_input("Senha atual", type="password")
        new_password = st.text_input("Nova senha", type="password")
        confirmation = st.text_input("Confirme a nova senha", type="password")
        save_password = st.form_submit_button(
            "Alterar senha",
            type="primary",
        )

    if save_password:
        if new_password != confirmation:
            st.error("As senhas não coincidem.")
        else:
            try:
                change_password(user.id, current_password, new_password)
                st.success("Senha alterada com segurança.")
            except AuthError as exc:
                st.error(str(exc))

with access_tab:
    st.markdown("#### Situação do acesso")
    st.success("Aprovado e ativo")
    st.write(
        "O administrador pode bloquear o acesso ou enviar um link temporário "
        "de redefinição, mas não consegue visualizar sua senha."
    )
    st.markdown("#### Encerrar sessão")
    if st.button("Sair da LEX AI", type="secondary"):
        sign_out()
        st.rerun()

render_footer()
