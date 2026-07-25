import os

import streamlit as st

from utils.footer import render_footer
from utils.page_style import apply_page_style, render_page_heading
from utils.session import (
    auth_url,
    logout_url,
    prepare_application,
    require_user,
)


st.set_page_config(
    page_title="Acesso | LEX AI",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()
prepare_application()
user = require_user()
render_page_heading(
    "Conta única",
    "Acesso integrado",
    (
        "Sua conta aprovada na LEX AI também dá acesso à FISCUS AI. "
        "A sessão, a senha e a situação cadastral são compartilhadas."
    ),
)

left, center, right = st.columns([1, 2, 1])
with center:
    st.success(f"Conectado(a) como {user.full_name}.")
    st.page_link(
        "pages/4_👤_Minha_Conta.py",
        label="Gerenciar minha conta",
        icon="👤",
        use_container_width=True,
    )
    st.link_button(
        "Abrir a FISCUS AI",
        os.getenv(
            "FISCUS_PUBLIC_URL",
            "https://fiscus.54-94-43-149.sslip.io",
        ),
        icon="⚖️",
        use_container_width=True,
    )
    st.link_button(
        "Encerrar sessão nas duas plataformas",
        logout_url(),
        icon="↪️",
        use_container_width=True,
    )

st.html(
    '<div class="lex-note" style="margin-top:32px">'
    "<strong>Proteção da conta:</strong> a senha não é armazenada em texto "
    "legível. O administrador pode aprovar, bloquear ou iniciar uma "
    "redefinição, mas nunca consegue consultar sua senha."
    "</div>"
)

render_footer()
