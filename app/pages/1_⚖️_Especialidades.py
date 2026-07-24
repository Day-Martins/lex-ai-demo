import streamlit as st

from utils.footer import render_footer
from utils.page_style import apply_page_style, render_page_heading


st.set_page_config(
    page_title="Especialidades | LEX AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()
render_page_heading(
    "Especialidades",
    "Inteligências jurídicas por área",
    (
        "Escolha uma especialidade para conhecer os recursos, as fontes e os "
        "limites do ambiente jurídico correspondente."
    ),
)

left, center, right = st.columns([1, 2, 1])
with center:
    st.html(
        """
        <div class="lex-panel">
            <div class="lex-status">Disponível</div>
            <h2 style="margin:18px 0 12px 0">
                Direito Tributário · Fiscus AI
            </h2>
            <p style="color:#C7CDD6;line-height:1.75;margin:0">
                Reforma Tributária, pesquisa em fontes oficiais, análise
                documental, simulações auditáveis e monitor legislativo.
            </p>
        </div>
        """
    )
    st.page_link(
        "pages/2_↳_Direito_Tributário_·_Fiscus_AI.py",
        label="Conhecer a especialidade",
        icon="⚖️",
        use_container_width=True,
    )

st.html(
    """
    <div class="lex-note" style="margin-top:36px">
        Novas especialidades serão adicionadas gradualmente e aparecerão
        agrupadas logo abaixo de <strong>Especialidades</strong> no menu.
    </div>
    """
)

render_footer()
