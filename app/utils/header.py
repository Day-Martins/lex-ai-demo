import base64
from pathlib import Path

import streamlit as st


CORES = {
    "preto_juridico": "#0B0F14",
    "azul_noturno": "#111827",
    "dourado_institucional": "#C9A227",
    "dourado_claro": "#D8B45A",
    "branco_gelo": "#F5F7FA",
    "cinza_juridico": "#9CA3AF",
}


def _imagem_em_base64(caminho: str) -> str | None:
    """
    Converte uma imagem local para Base64.

    Retorna None quando o arquivo não existe.
    """
    arquivo = Path(caminho)

    if not arquivo.exists():
        return None

    try:
        with arquivo.open("rb") as imagem:
            return base64.b64encode(imagem.read()).decode("utf-8")
    except OSError:
        return None


def render_header(
    titulo: str = "LEX AI",
    subtitulo: str = "Plataforma de Inteligência Jurídica Especializada",
    logo_path: str = "assets/logo_lex.png",
    mostrar_status: bool = True,
    status_texto: str = "Plataforma em evolução",
) -> None:
    """
    Renderiza o cabeçalho institucional da LEX AI.
    """

    logo_base64 = _imagem_em_base64(logo_path)

    if logo_base64:
        elemento_logo = f"""
            <img
                src="data:image/png;base64,{logo_base64}"
                class="lex-header-logo"
                alt="Logo da LEX AI"
            >
        """
    else:
        elemento_logo = """
            <div class="lex-header-logo-placeholder">
                L
            </div>
        """

    if mostrar_status:
        elemento_status = f"""
            <div class="lex-header-status">
                <span class="lex-header-status-dot"></span>
                {status_texto}
            </div>
        """
    else:
        elemento_status = ""

    st.markdown(
        f"""
        <style>
            .lex-header {{
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 24px;
                padding: 14px 4px 24px 4px;
                margin-bottom: 34px;
                border-bottom: 1px solid rgba(201, 162, 39, 0.20);
            }}

            .lex-header-brand {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}

            .lex-header-logo {{
                width: 64px;
                height: 64px;
                object-fit: contain;
            }}

            .lex-header-logo-placeholder {{
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 16px;
                border: 1px solid rgba(201, 162, 39, 0.45);
                background: rgba(201, 162, 39, 0.08);
                color: {CORES["dourado_claro"]};
                font-size: 26px;
                font-weight: 900;
            }}

            .lex-header-title {{
                color: {CORES["branco_gelo"]};
                font-size: 23px;
                font-weight: 900;
                letter-spacing: 0.08em;
                line-height: 1.1;
            }}

            .lex-header-subtitle {{
                color: {CORES["cinza_juridico"]};
                font-size: 13px;
                line-height: 1.45;
                margin-top: 5px;
            }}

            .lex-header-status {{
                display: inline-flex;
                align-items: center;
                gap: 9px;
                padding: 9px 14px;
                border-radius: 999px;
                border: 1px solid rgba(201, 162, 39, 0.32);
                background: rgba(201, 162, 39, 0.07);
                color: {CORES["dourado_claro"]};
                font-size: 12px;
                font-weight: 750;
                white-space: nowrap;
            }}

            .lex-header-status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: {CORES["dourado_institucional"]};
                box-shadow: 0 0 12px rgba(201, 162, 39, 0.80);
            }}

            @media (max-width: 760px) {{
                .lex-header {{
                    align-items: flex-start;
                }}

                .lex-header-status {{
                    display: none;
                }}

                .lex-header-logo {{
                    width: 52px;
                    height: 52px;
                }}

                .lex-header-logo-placeholder {{
                    width: 50px;
                    height: 50px;
                }}

                .lex-header-title {{
                    font-size: 20px;
                }}

                .lex-header-subtitle {{
                    font-size: 12px;
                }}
            }}
        </style>

        <header class="lex-header">
            <div class="lex-header-brand">
                {elemento_logo}

                <div>
                    <div class="lex-header-title">
                        {titulo}
                    </div>

                    <div class="lex-header-subtitle">
                        {subtitulo}
                    </div>
                </div>
            </div>

            {elemento_status}
        </header>
        """,
        unsafe_allow_html=True,
    )