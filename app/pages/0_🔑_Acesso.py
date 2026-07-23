import streamlit as st

from utils.access_forms import render_access_portal
from utils.footer import render_footer
from utils.page_style import apply_page_style, render_page_heading


st.set_page_config(
    page_title="Acesso | LEX AI",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()
render_page_heading(
    "Acesso seguro",
    "Entrar ou solicitar cadastro",
    (
        "Crie sua conta com dados básicos. Novos cadastros permanecem "
        "pendentes até a análise do administrador da LEX AI."
    ),
)

left, center, right = st.columns([1, 2, 1])
with center:
    render_access_portal()

st.html(
    """
    <div class="lex-note" style="margin-top:32px">
        <strong>Proteção da sua senha:</strong> a LEX AI não armazena a senha
        em texto legível. O administrador pode aprovar, bloquear ou iniciar
        uma redefinição por e-mail, mas nunca consegue consultar sua senha.
    </div>
    """
)

render_footer()
