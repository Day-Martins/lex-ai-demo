import streamlit as st

from utils.footer import render_footer
from utils.page_style import (
    apply_page_style,
    render_feature_card,
    render_page_heading,
)


st.set_page_config(
    page_title="Especialidades | LEX AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()

render_page_heading(
    "Especialidades · Direito Tributário",
    "Fiscus AI",
    (
        "Plataforma especializada na Reforma Tributária brasileira para apoiar "
        "profissionais jurídicos, fiscais e contábeis com pesquisa, análise "
        "documental, simulações auditáveis e consulta a fontes oficiais."
    ),
)

hero_left, hero_right = st.columns([1.45, 1], gap="large")
with hero_left:
    st.html(
        """
        <div class="lex-panel">
            <div class="lex-status">Disponível</div>
            <h2 style="margin:18px 0 12px 0">
                Conhecimento tributário organizado para decisões mais seguras
            </h2>
            <p style="color:#C7CDD6;line-height:1.75;margin:0">
                A Fiscus AI reúne um assistente especializado, base legal,
                monitor legislativo, análise de documentos e calculadoras.
                Cada resultado explicita premissas e limitações para facilitar
                a revisão do profissional responsável.
            </p>
        </div>
        """
    )

with hero_right:
    st.markdown("#### Para quem é")
    st.markdown(
        """
        - Advogados e escritórios
        - Consultores e departamentos jurídicos
        - Contadores e profissionais fiscais
        - Empresas em preparação para a Reforma Tributária
        - Estudantes e pesquisadores de Direito Tributário
        """
    )
    st.link_button(
        "Acessar a Fiscus AI",
        "https://fiscus.54-94-43-149.sslip.io/",
        type="primary",
        use_container_width=True,
    )

st.markdown("## Recursos disponíveis na Fiscus AI")
st.caption(
    "As funcionalidades abaixo correspondem à implementação atual da "
    "plataforma e exigem validação profissional antes do uso decisório."
)

features = (
    (
        "🤖",
        "Assistente tributário",
        (
            "Responde sobre CBS, IBS, Imposto Seletivo e impactos da Reforma "
            "Tributária com recuperação de conhecimento e indicação de fontes."
        ),
    ),
    (
        "🧮",
        "Calculadora 2026–2033",
        (
            "Simula a transição tributária, compara cenários de CBS e IBS, "
            "registra premissas e exporta a memória de cálculo."
        ),
    ),
    (
        "📁",
        "Análise de documentos",
        (
            "Classifica documentos, extrai dados, identifica tributos, riscos "
            "e pontos de revisão sem tratar anexos como instruções confiáveis."
        ),
    ),
    (
        "📄",
        "Relatórios exportáveis",
        (
            "Gera diagnósticos de impacto em PDF e DOCX com dados declarados, "
            "cenários hipotéticos, fundamentação e ressalvas profissionais."
        ),
    ),
    (
        "🔄",
        "Monitor e base legal",
        (
            "Organiza legislação e atualizações de fontes oficiais em uma fila "
            "de revisão para manter o conhecimento tributário rastreável."
        ),
    ),
    (
        "🧭",
        "Dossiê patrimonial",
        (
            "Consolida evidências, simulações e minutas de diagnóstico ou "
            "resumo executivo para revisão jurídica, contábil e tributária."
        ),
    ),
)

for row_start in range(0, len(features), 3):
    columns = st.columns(3, gap="large")
    for column, feature in zip(columns, features[row_start : row_start + 3]):
        with column:
            render_feature_card(*feature)

st.markdown("## Como usar no dia a dia")
step_1, step_2, step_3 = st.columns(3, gap="large")
with step_1:
    st.markdown("### 1. Contextualize")
    st.write(
        "Informe o setor, o tributo, o período, as premissas e o objetivo da "
        "consulta. Evite dados pessoais ou documentos sigilosos desnecessários."
    )
with step_2:
    st.markdown("### 2. Examine as evidências")
    st.write(
        "Consulte as fontes apresentadas, confira a memória dos cálculos e "
        "diferencie fatos documentais de hipóteses ou dados declarados."
    )
with step_3:
    st.markdown("### 3. Valide")
    st.write(
        "Confirme vigência, enquadramento e texto oficial antes de utilizar o "
        "resultado em parecer, contrato, apuração ou decisão empresarial."
    )

st.markdown("## Exemplos de uso")
examples = (
    "Explique a diferença entre IBS e CBS e indique as fontes aplicáveis.",
    "Simule a transição de 2026 a 2033 e detalhe a memória de cálculo.",
    "Analise este documento e separe evidências, riscos e dados ausentes.",
    "Gere um diagnóstico preliminar de impacto para revisão profissional.",
    "Organize um dossiê patrimonial com cenários e ressalvas jurídicas.",
)
for example in examples:
    st.code(example, language=None)

st.markdown("## Limites e uso responsável")
st.html(
    """
    <div class="lex-note">
        A Fiscus AI é uma ferramenta de apoio e não substitui advogado,
        contador, parecer jurídico, apuração fiscal, consulta formal à
        administração tributária ou conferência da legislação vigente.
        Simulações e análises dependem das premissas e dos documentos
        informados. A conclusão e o uso da informação permanecem sob
        responsabilidade do profissional habilitado.
    </div>
    """
)

render_footer()
