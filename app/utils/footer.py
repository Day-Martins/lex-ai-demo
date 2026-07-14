import base64
from datetime import datetime
from pathlib import Path
from textwrap import dedent

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
    arquivo = Path(caminho)

    if not arquivo.exists():
        return None

    try:
        with arquivo.open("rb") as imagem:
            return base64.b64encode(imagem.read()).decode("utf-8")
    except OSError:
        return None


def render_footer(
    logo_path: str = "assets/logo_dmt.png",
    nome_plataforma: str = "LEX AI",
    descricao: str = "Plataforma de Inteligência Jurídica Especializada",
) -> None:
    """
    Renderiza o rodapé institucional da plataforma.
    """

    ano_atual = datetime.now().year
    logo_base64 = _imagem_em_base64(logo_path)

    if logo_base64:
        elemento_logo = f"""
            <img
                src="data:image/png;base64,{logo_base64}"
                class="lex-footer-logo"
                alt="Marca institucional"
            >
        """
    else:
        elemento_logo = ""

    html_rodape = f"""
        <style>
            .lex-footer {{
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 24px;
                margin-top: 72px;
                padding: 30px 4px 15px 4px;
                border-top: 1px solid rgba(201, 162, 39, 0.20);
            }}

            .lex-footer-brand {{
                color: {CORES["branco_gelo"]};
                font-size: 18px;
                font-weight: 850;
                letter-spacing: 0.04em;
            }}

            .lex-footer-description {{
                color: {CORES["cinza_juridico"]};
                font-size: 14px;
                line-height: 1.55;
                margin-top: 5px;
            }}

            .lex-footer-copy {{
                color: {CORES["cinza_juridico"]};
                font-size: 12px;
                margin-top: 5px;
            }}

            .lex-footer-logo {{
                max-width: 190px;
                max-height: 58px;
                object-fit: contain;
                opacity: 0.90;
            }}

            @media (max-width: 700px) {{
                .lex-footer {{
                    flex-direction: column;
                    align-items: flex-start;
                }}
            }}
        </style>

        <footer class="lex-footer">
            <div>
                <div class="lex-footer-brand">
                    {nome_plataforma}
                </div>

                <div class="lex-footer-description">
                    {descricao}
                </div>

                <div class="lex-footer-copy">
                    © {ano_atual} — Todos os direitos reservados.
                </div>
            </div>

            <div>
                {elemento_logo}
            </div>
        </footer>
        """
    html_rodape = "\n".join(
        linha.strip()
        for linha in dedent(html_rodape).splitlines()
        if linha.strip()
    )
    st.html(html_rodape)
