import base64
from pathlib import Path
from textwrap import dedent

import streamlit as st

from utils.footer import render_footer


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="LEX AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DIRETÓRIOS E IMAGENS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]


def get_base64(file_path: Path) -> str | None:
    """
    Converte uma imagem local em Base64.

    Retorna None caso o arquivo não exista ou não possa ser lido.
    """
    if not file_path.exists():
        return None

    try:
        with file_path.open("rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except OSError:
        return None


logo_lex = get_base64(BASE_DIR / "assets" / "lex_neutro.png")


def render_html(markup: str, **_: object) -> None:
    """Renderiza HTML sem submetê-lo ao parser Markdown."""
    markup_continuo = "\n".join(
        linha.strip()
        for linha in dedent(markup).splitlines()
        if linha.strip()
    )
    st.html(markup_continuo)


# =========================================================
# CSS GLOBAL
# =========================================================

render_html(
    """
<style>
:root {
    --preto-juridico: #0B0F14;
    --azul-noturno: #111827;
    --dourado-institucional: #C9A227;
    --dourado-claro: #D8B45A;
    --branco-gelo: #F5F7FA;
    --cinza-juridico: #9CA3AF;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at top right,
            rgba(201, 162, 39, 0.08),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            var(--preto-juridico) 0%,
            var(--azul-noturno) 100%
        );
}

[data-testid="stHeader"] {
    background: var(--preto-juridico);
    border-bottom: 1px solid rgba(201, 162, 39, 0.18);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080D13 0%, #0B1421 100%);
    border-right: 1px solid rgba(201, 162, 39, 0.30);
}

[data-testid="stSidebar"] * {
    color: var(--branco-gelo) !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 9px;
    margin-bottom: 5px;
}

[data-testid="stSidebarNav"] a:hover {
    background: rgba(201, 162, 39, 0.10);
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(201, 162, 39, 0.16);
    border-left: 3px solid var(--dourado-institucional);
}

.block-container {
    max-width: 1180px;
    padding-top: 3rem;
    padding-bottom: 8rem;
}

h1,
h2,
h3,
p,
li {
    color: var(--branco-gelo);
}

.lex-logo-container {
    text-align: center;
    margin-bottom: 12px;
}

.lex-logo {
    width: 145px;
    max-height: 150px;
    object-fit: contain;
}

.lex-logo-fallback {
    display: inline-flex;
    width: 90px;
    height: 90px;
    align-items: center;
    justify-content: center;
    border-radius: 24px;
    border: 1px solid rgba(201, 162, 39, 0.45);
    background: rgba(201, 162, 39, 0.07);
    color: var(--dourado-claro);
    font-family: Georgia, serif;
    font-size: 46px;
    font-weight: 900;
}

.main-title {
    text-align: center;
    font-family: Georgia, serif;
    font-size: 72px;
    font-weight: 800;
    letter-spacing: 9px;
    color: var(--branco-gelo);
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: var(--dourado-institucional);
    font-size: 18px;
    text-transform: uppercase;
    letter-spacing: 4px;
    font-weight: 900;
    margin-bottom: 24px;
}

.divider {
    height: 2px;
    width: 55%;
    margin: 28px auto;
    background: linear-gradient(
        90deg,
        transparent,
        var(--dourado-institucional),
        transparent
    );
}

.intro {
    text-align: center;
    font-size: 20px;
    line-height: 1.8;
    color: #E5E7EB;
    max-width: 900px;
    margin: 0 auto 34px auto;
}

.badges-container {
    text-align: center;
    margin-bottom: 46px;
}

.badge {
    display: inline-block;
    border: 1px solid rgba(201, 162, 39, 0.42);
    color: var(--branco-gelo);
    padding: 10px 16px;
    border-radius: 999px;
    font-size: 15px;
    background: rgba(255, 255, 255, 0.035);
    margin: 6px;
}

.section-kicker {
    text-align: center;
    color: var(--dourado-claro);
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 52px;
    margin-bottom: 10px;
}

.section-title {
    text-align: center;
    color: var(--branco-gelo);
    font-size: 36px;
    font-weight: 850;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.section-description {
    text-align: center;
    color: var(--cinza-juridico);
    font-size: 18px;
    line-height: 1.7;
    max-width: 780px;
    margin: 0 auto 34px auto;
}

.specialty-card {
    box-sizing: border-box;
    width: 100%;
    min-height: 350px;
    padding: 30px;
    background: linear-gradient(145deg, #131D2C 0%, #0D1521 100%);
    border: 1px solid rgba(201, 162, 39, 0.30);
    border-top: 4px solid var(--dourado-institucional);
    border-radius: 20px;
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.26);
    transition:
        transform 0.20s ease,
        border-color 0.20s ease,
        box-shadow 0.20s ease;
}

.specialty-card:hover {
    transform: translateY(-4px);
    border-color: rgba(216, 180, 90, 0.48);
    box-shadow: 0 20px 42px rgba(0, 0, 0, 0.34);
}

.specialty-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 58px;
    height: 58px;
    margin-bottom: 22px;
    border-radius: 15px;
    border: 1px solid rgba(201, 162, 39, 0.34);
    background: rgba(201, 162, 39, 0.08);
    color: var(--dourado-claro);
    font-size: 27px;
}

.status {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    padding: 7px 11px;
    margin-bottom: 20px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.status-available {
    color: var(--dourado-claro);
    border: 1px solid rgba(201, 162, 39, 0.42);
    background: rgba(201, 162, 39, 0.09);
}

.status-development {
    color: var(--cinza-juridico);
    border: 1px solid rgba(156, 163, 175, 0.28);
    background: rgba(156, 163, 175, 0.07);
}

.specialty-title {
    color: var(--branco-gelo);
    font-size: 24px;
    line-height: 1.25;
    font-weight: 900;
    margin-bottom: 8px;
}

.specialty-name {
    color: var(--dourado-claro);
    font-size: 16px;
    font-weight: 850;
    margin-bottom: 18px;
}

.specialty-text {
    color: #C7CDD6;
    font-size: 16px;
    line-height: 1.75;
}

.stButton > button,
.stLinkButton > a {
    width: 100%;
    min-height: 48px;
    border-radius: 11px;
    font-size: 16px;
    font-weight: 850;
    transition: all 0.20s ease;
}

.stButton > button[kind="primary"],
.stLinkButton > a[kind="primary"] {
    color: var(--preto-juridico) !important;
    background: linear-gradient(
        135deg,
        var(--dourado-claro),
        var(--dourado-institucional)
    ) !important;
    border: 1px solid var(--dourado-claro) !important;
}

.stButton > button[kind="primary"]:hover,
.stLinkButton > a[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(201, 162, 39, 0.24);
}

.stButton > button[kind="secondary"] {
    color: var(--branco-gelo) !important;
    background: rgba(255, 255, 255, 0.035) !important;
    border: 1px solid rgba(201, 162, 39, 0.32) !important;
}

.stButton > button:disabled {
    color: var(--cinza-juridico) !important;
    opacity: 0.65;
}

.update-card {
    background: linear-gradient(
        145deg,
        rgba(17, 24, 39, 0.97),
        rgba(11, 15, 20, 0.97)
    );
    border: 1px solid rgba(201, 162, 39, 0.24);
    border-left: 5px solid var(--dourado-institucional);
    border-radius: 18px;
    padding: 26px 28px;
    margin-bottom: 18px;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.20);
}

.update-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.update-area {
    display: inline-block;
    color: var(--dourado-claro);
    background: rgba(201, 162, 39, 0.08);
    border: 1px solid rgba(201, 162, 39, 0.32);
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.update-date {
    color: var(--cinza-juridico);
    font-size: 14px;
    font-weight: 700;
}

.update-title {
    color: var(--branco-gelo);
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 10px;
}

.update-text {
    color: #C7CDD6;
    font-size: 16px;
    line-height: 1.75;
}

.update-impact {
    color: #E5E7EB;
    font-size: 15px;
    line-height: 1.65;
    margin-top: 16px;
    padding: 13px 15px;
    border-radius: 10px;
    border: 1px solid rgba(201, 162, 39, 0.18);
    background: rgba(201, 162, 39, 0.05);
}

.update-impact strong {
    color: var(--dourado-claro);
}

.update-source {
    color: var(--cinza-juridico);
    font-size: 13px;
    margin-top: 16px;
}

.benefit-card {
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(201, 162, 39, 0.20);
    border-radius: 17px;
    padding: 24px;
    min-height: 215px;
}

.benefit-number {
    color: rgba(216, 180, 90, 0.38);
    font-size: 30px;
    font-weight: 900;
    margin-bottom: 16px;
}

.benefit-title {
    color: var(--branco-gelo);
    font-size: 19px;
    font-weight: 900;
    margin-bottom: 9px;
}

.benefit-text {
    color: var(--cinza-juridico);
    font-size: 15px;
    line-height: 1.7;
}

.notice {
    margin-top: 48px;
    padding: 22px 25px;
    border-radius: 16px;
    border: 1px solid rgba(201, 162, 39, 0.24);
    background: rgba(201, 162, 39, 0.055);
}

.notice-title {
    color: var(--dourado-claro);
    font-size: 16px;
    font-weight: 900;
    margin-bottom: 8px;
}

.notice-text {
    color: var(--cinza-juridico);
    font-size: 14px;
    line-height: 1.65;
}

@media (max-width: 850px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        font-size: 48px;
        letter-spacing: 5px;
    }

    .subtitle {
        font-size: 15px;
        letter-spacing: 2px;
    }

    .intro {
        font-size: 16px;
    }

    .update-top {
        align-items: flex-start;
        flex-direction: column;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# IDENTIDADE DA LEX AI
# =========================================================

if logo_lex:
    render_html(
        f"""
<div class="lex-logo-container">
    <img
        src="data:image/png;base64,{logo_lex}"
        class="lex-logo"
        alt="LEX AI"
    >
</div>
""",
        unsafe_allow_html=True,
    )
else:
    render_html(
        """
<div class="lex-logo-container">
    <div class="lex-logo-fallback">L</div>
</div>
""",
        unsafe_allow_html=True,
    )

render_html(
    '<div class="main-title">LEX AI</div>',
    unsafe_allow_html=True,
)

render_html(
    """
<div class="subtitle">
    Plataforma de Inteligência Jurídica Especializada
</div>
""",
    unsafe_allow_html=True,
)

render_html(
    '<div class="divider"></div>',
    unsafe_allow_html=True,
)

render_html(
    """
<div class="intro">
A LEX AI reúne inteligências artificiais especializadas em diferentes
ramos do Direito. Cada ambiente possui regras, fontes e conhecimentos
próprios, oferecendo uma experiência jurídica mais precisa, organizada
e segura.
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# BADGES
# =========================================================

render_html(
    """
<div class="badges-container">
    <span class="badge">Inteligência Jurídica</span>
    <span class="badge">Especialização por Área</span>
    <span class="badge">Fontes Verificáveis</span>
    <span class="badge">Atualização Legislativa</span>
    <span class="badge">Segurança</span>
    <span class="badge">Controle de Escopo</span>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# ESPECIALIDADES
# =========================================================

render_html(
    """
<div class="section-kicker">
    Especialidades
</div>

<div class="section-title">
    Escolha a inteligência jurídica
</div>

<div class="section-description">
    Cada especialidade funciona em um ambiente próprio, com base de
    conhecimento, instruções e limites específicos.
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    render_html(
        """
<div class="specialty-card">
    <div class="specialty-icon">⚖️</div>
    <div class="status status-available">
        Disponível
    </div>
    <div class="specialty-title">
        Direito Tributário
    </div>
    <div class="specialty-name">
        Fiscus AI
    </div>
    <div class="specialty-text">
        Inteligência especializada em Reforma Tributária,
        IBS, CBS, Imposto Seletivo, legislação, jurisprudência,
        soluções de consulta e estratégias tributárias.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.link_button(
        "Acessar Fiscus AI",
        "https://fiscus.54-94-43-149.sslip.io/",
        type="primary",
        width="stretch",
        key="acessar_fiscus",
    )

with c2:
    render_html(
        """
<div class="specialty-card">
    <div class="specialty-icon">👷</div>
    <div class="status status-development">
        Em desenvolvimento
    </div>
    <div class="specialty-title">
        Direito Trabalhista
    </div>
    <div class="specialty-name">
        Nova especialidade
    </div>
    <div class="specialty-text">
        Ambiente especializado em legislação trabalhista,
        relações de trabalho, contratos, obrigações e
        entendimentos jurisprudenciais.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.button(
        "Em breve",
        disabled=True,
        use_container_width=True,
        key="trabalhista_em_breve",
    )

with c3:
    render_html(
        """
<div class="specialty-card">
    <div class="specialty-icon">§</div>
    <div class="status status-development">
        Em desenvolvimento
    </div>
    <div class="specialty-title">
        Direito Civil
    </div>
    <div class="specialty-name">
        Nova especialidade
    </div>
    <div class="specialty-text">
        Inteligência dedicada a contratos, obrigações,
        responsabilidade civil, relações privadas e
        demais matérias cíveis.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.button(
        "Em breve",
        disabled=True,
        use_container_width=True,
        key="civil_em_breve",
    )


# =========================================================
# ATUALIZAÇÕES
# =========================================================

render_html(
    """
<div class="section-kicker">
    Monitoramento jurídico
</div>

<div class="section-title">
    Atualizações em destaque
</div>

<div class="section-description">
    Alterações legislativas e informações relevantes organizadas
    conforme a área jurídica correspondente.
</div>
""",
    unsafe_allow_html=True,
)

render_html(
    """
<div class="update-card">
    <div class="update-top">
        <div class="update-area">
            Institucional
        </div>

        <div class="update-date">
            14 de julho de 2026
        </div>
    </div>

    <div class="update-title">
        Estrutura inicial da LEX AI
    </div>

    <div class="update-text">
        A plataforma central está sendo preparada para integrar
        inteligências artificiais especializadas em diferentes
        ramos do Direito.
    </div>

    <div class="update-impact">
        <strong>Impacto:</strong>
        criação da navegação central, identidade visual,
        especialidades jurídicas e área de monitoramento legislativo.
    </div>

    <div class="update-source">
        Fonte: LEX AI
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# DIFERENCIAIS
# =========================================================

render_html(
    """
<div class="section-kicker">
    Nossa proposta
</div>

<div class="section-title">
    Tecnologia jurídica com responsabilidade
</div>

<div class="section-description">
    A plataforma foi concebida para apoiar a pesquisa e a análise
    jurídica, preservando a responsabilidade técnica do profissional.
</div>
""",
    unsafe_allow_html=True,
)

b1, b2, b3, b4 = st.columns(4, gap="medium")

with b1:
    render_html(
        """
<div class="benefit-card">
    <div class="benefit-number">01</div>

    <div class="benefit-title">
        Especialização
    </div>

    <div class="benefit-text">
        Cada inteligência atua em um ramo jurídico delimitado,
        com instruções e contexto específicos.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with b2:
    render_html(
        """
<div class="benefit-card">
    <div class="benefit-number">02</div>

    <div class="benefit-title">
        Fundamentação
    </div>

    <div class="benefit-text">
        Priorização de legislação, fontes oficiais e documentos
        jurídicos verificáveis.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with b3:
    render_html(
        """
<div class="benefit-card">
    <div class="benefit-number">03</div>

    <div class="benefit-title">
        Segurança
    </div>

    <div class="benefit-text">
        Estrutura preparada para controle de acesso,
        segregação das bases e proteção das consultas.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

with b4:
    render_html(
        """
<div class="benefit-card">
    <div class="benefit-number">04</div>

    <div class="benefit-title">
        Atualização
    </div>

    <div class="benefit-text">
        Organização das alterações legislativas conforme
        cada especialidade jurídica.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# AVISO DE RESPONSABILIDADE
# =========================================================

render_html(
    """
<div class="notice">
    <div class="notice-title">
        ⚠️ Aviso de responsabilidade
    </div>

    <div class="notice-text">
        A LEX AI é uma ferramenta de apoio à pesquisa, organização
        e análise jurídica. As informações apresentadas não substituem
        a conferência das fontes oficiais, a avaliação profissional ou
        a análise das particularidades de cada caso concreto.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# RODAPÉ
# =========================================================

render_footer()
