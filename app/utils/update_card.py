from html import escape

import streamlit as st


CORES = {
    "preto_juridico": "#0B0F14",
    "azul_noturno": "#111827",
    "dourado_institucional": "#C9A227",
    "dourado_claro": "#D8B45A",
    "branco_gelo": "#F5F7FA",
    "cinza_juridico": "#9CA3AF",
}


def render_update_card(
    titulo: str,
    resumo: str,
    area: str,
    data_publicacao: str,
    fonte: str,
    impacto: str | None = None,
    url_fonte: str | None = None,
) -> None:
    """
    Renderiza uma atualização legislativa ou jurídica.
    """

    titulo_seguro = escape(titulo)
    resumo_seguro = escape(resumo)
    area_segura = escape(area)
    data_segura = escape(data_publicacao)
    fonte_segura = escape(fonte)

    if impacto:
        impacto_html = f"""
            <div class="lex-update-impact">
                <strong>Impacto:</strong> {escape(impacto)}
            </div>
        """
    else:
        impacto_html = ""

    if url_fonte:
        url_segura = escape(url_fonte, quote=True)

        fonte_html = f"""
            <a
                href="{url_segura}"
                target="_blank"
                rel="noopener noreferrer"
                class="lex-update-source"
            >
                Consultar fonte oficial ↗
            </a>
        """
    else:
        fonte_html = f"""
            <span class="lex-update-source">
                {fonte_segura}
            </span>
        """

    st.html(
        f"""
        <style>
            .lex-update-card {{
                position: relative;
                overflow: hidden;
                padding: 25px 27px;
                margin-bottom: 16px;
                border-radius: 18px;
                border: 1px solid rgba(156, 163, 175, 0.16);
                border-left: 4px solid {CORES["dourado_institucional"]};
                background:
                    linear-gradient(
                        135deg,
                        rgba(17, 24, 39, 0.96),
                        rgba(11, 15, 20, 0.96)
                    );
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
                transition:
                    transform 0.20s ease,
                    border-color 0.20s ease;
            }}

            .lex-update-card:hover {{
                transform: translateY(-3px);
                border-color: rgba(201, 162, 39, 0.40);
            }}

            .lex-update-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 18px;
                margin-bottom: 15px;
            }}

            .lex-update-area {{
                display: inline-flex;
                width: fit-content;
                padding: 6px 10px;
                border-radius: 999px;
                border: 1px solid rgba(201, 162, 39, 0.28);
                background: rgba(201, 162, 39, 0.08);
                color: {CORES["dourado_claro"]};
                font-size: 10px;
                font-weight: 850;
                letter-spacing: 0.07em;
                text-transform: uppercase;
            }}

            .lex-update-date {{
                color: {CORES["cinza_juridico"]};
                font-size: 11px;
                font-weight: 700;
                white-space: nowrap;
            }}

            .lex-update-title {{
                color: {CORES["branco_gelo"]};
                font-size: 18px;
                font-weight: 850;
                line-height: 1.35;
                margin-bottom: 10px;
            }}

            .lex-update-summary {{
                color: {CORES["cinza_juridico"]};
                font-size: 13px;
                line-height: 1.7;
            }}

            .lex-update-impact {{
                margin-top: 15px;
                padding: 12px 14px;
                border-radius: 11px;
                border: 1px solid rgba(201, 162, 39, 0.18);
                background: rgba(201, 162, 39, 0.05);
                color: #D1D5DB;
                font-size: 12px;
                line-height: 1.55;
            }}

            .lex-update-impact strong {{
                color: {CORES["dourado_claro"]};
            }}

            .lex-update-footer {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
                margin-top: 18px;
                padding-top: 15px;
                border-top: 1px solid rgba(156, 163, 175, 0.12);
            }}

            .lex-update-source-label {{
                color: {CORES["cinza_juridico"]};
                font-size: 10px;
            }}

            .lex-update-source {{
                color: {CORES["dourado_claro"]};
                font-size: 11px;
                font-weight: 750;
                text-decoration: none;
            }}

            .lex-update-source:hover {{
                color: {CORES["branco_gelo"]};
                text-decoration: none;
            }}

            @media (max-width: 650px) {{
                .lex-update-top,
                .lex-update-footer {{
                    align-items: flex-start;
                    flex-direction: column;
                }}
            }}
        </style>

        <article class="lex-update-card">
            <div class="lex-update-top">
                <div class="lex-update-area">
                    {area_segura}
                </div>

                <div class="lex-update-date">
                    {data_segura}
                </div>
            </div>

            <div class="lex-update-title">
                {titulo_seguro}
            </div>

            <div class="lex-update-summary">
                {resumo_seguro}
            </div>

            {impacto_html}

            <div class="lex-update-footer">
                <div class="lex-update-source-label">
                    Fonte: {fonte_segura}
                </div>

                {fonte_html}
            </div>
        </article>
        """
    )
