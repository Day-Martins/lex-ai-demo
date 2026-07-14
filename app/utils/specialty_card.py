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


def render_specialty_card(
    nome: str,
    produto: str,
    descricao: str,
    icone: str = "⚖",
    disponivel: bool = False,
    identificador: str | None = None,
) -> None:
    """
    Renderiza um card de especialidade jurídica.

    O botão deve ser criado na página que chama este componente,
    permitindo que cada página determine sua própria navegação.
    """

    nome_seguro = escape(nome)
    produto_seguro = escape(produto)
    descricao_segura = escape(descricao)
    icone_seguro = escape(icone)

    if disponivel:
        classe_status = "available"
        texto_status = "● Disponível"
    else:
        classe_status = "development"
        texto_status = "Em desenvolvimento"

    id_html = (
        f'id="{escape(identificador)}"'
        if identificador
        else ""
    )

    st.markdown(
        f"""
        <style>
            .lex-specialty-card {{
                min-height: 325px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                padding: 28px;
                border-radius: 20px;
                border: 1px solid rgba(156, 163, 175, 0.17);
                border-top: 3px solid {CORES["dourado_institucional"]};
                background:
                    linear-gradient(
                        145deg,
                        rgba(17, 24, 39, 0.98),
                        rgba(11, 15, 20, 0.96)
                    );
                box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22);
                transition:
                    transform 0.22s ease,
                    border-color 0.22s ease,
                    box-shadow 0.22s ease;
            }}

            .lex-specialty-card:hover {{
                transform: translateY(-5px);
                border-color: rgba(201, 162, 39, 0.42);
                box-shadow: 0 20px 44px rgba(0, 0, 0, 0.30);
            }}

            .lex-specialty-icon {{
                width: 56px;
                height: 56px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 22px;
                border-radius: 16px;
                border: 1px solid rgba(201, 162, 39, 0.34);
                background: rgba(201, 162, 39, 0.08);
                color: {CORES["dourado_claro"]};
                font-size: 26px;
                font-weight: 850;
            }}

            .lex-specialty-status {{
                display: inline-flex;
                width: fit-content;
                align-items: center;
                padding: 6px 10px;
                margin-bottom: 18px;
                border-radius: 999px;
                font-size: 10px;
                font-weight: 850;
                letter-spacing: 0.07em;
                text-transform: uppercase;
            }}

            .lex-specialty-status.available {{
                color: {CORES["dourado_claro"]};
                border: 1px solid rgba(201, 162, 39, 0.34);
                background: rgba(201, 162, 39, 0.08);
            }}

            .lex-specialty-status.development {{
                color: {CORES["cinza_juridico"]};
                border: 1px solid rgba(156, 163, 175, 0.22);
                background: rgba(156, 163, 175, 0.06);
            }}

            .lex-specialty-name {{
                color: {CORES["branco_gelo"]};
                font-size: 24px;
                font-weight: 850;
                line-height: 1.2;
                margin-bottom: 8px;
            }}

            .lex-specialty-product {{
                color: {CORES["dourado_claro"]};
                font-size: 14px;
                font-weight: 800;
                margin-bottom: 16px;
            }}

            .lex-specialty-description {{
                color: {CORES["cinza_juridico"]};
                font-size: 14px;
                line-height: 1.7;
            }}
        </style>

        <article class="lex-specialty-card" {id_html}>
            <div>
                <div class="lex-specialty-icon">
                    {icone_seguro}
                </div>

                <div class="lex-specialty-status {classe_status}">
                    {texto_status}
                </div>

                <div class="lex-specialty-name">
                    {nome_seguro}
                </div>

                <div class="lex-specialty-product">
                    {produto_seguro}
                </div>

                <div class="lex-specialty-description">
                    {descricao_segura}
                </div>
            </div>
        </article>
        """,
        unsafe_allow_html=True,
    )