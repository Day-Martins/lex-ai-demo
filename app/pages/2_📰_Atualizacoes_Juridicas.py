from datetime import datetime, timedelta, timezone

import streamlit as st

from services.legislative_update_service import (
    REFERENCE_PORTALS,
    UpdateFetchResult,
    fetch_legal_updates,
)
from utils.footer import render_footer
from utils.page_style import apply_page_style, render_page_heading
from utils.update_card import render_update_card


st.set_page_config(
    page_title="Atualizações Jurídicas | LEX AI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()


@st.cache_data(ttl=1800, show_spinner=False)
def load_updates() -> UpdateFetchResult:
    return fetch_legal_updates()


render_page_heading(
    "Monitoramento jurídico",
    "Atualizações Jurídicas",
    (
        "Notícias, julgados e movimentações legislativas reunidos a partir "
        "de canais oficiais. Use os filtros para localizar o que é mais "
        "relevante para sua área e sempre consulte a publicação original."
    ),
)

with st.spinner("Consultando fontes oficiais..."):
    result = load_updates()

if result.unavailable_sources:
    st.info(
        "Algumas fontes estão temporariamente indisponíveis: "
        + ", ".join(result.unavailable_sources)
        + ". As demais atualizações continuam visíveis."
    )

filter_1, filter_2, filter_3 = st.columns([1.6, 1, 1], gap="medium")
with filter_1:
    query = st.text_input(
        "Pesquisar",
        placeholder="Tema, norma, tribunal ou palavra-chave",
    ).strip()
with filter_2:
    areas = sorted({update.area for update in result.updates})
    selected_area = st.selectbox("Área", ["Todas", *areas])
with filter_3:
    period_label = st.selectbox(
        "Período",
        ("Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todo o feed"),
        index=1,
    )

source_options = sorted({update.source for update in result.updates})
selected_sources = st.multiselect(
    "Fontes",
    source_options,
    default=source_options,
    placeholder="Selecione uma ou mais fontes",
)

period_days = {
    "Últimos 7 dias": 7,
    "Últimos 30 dias": 30,
    "Últimos 90 dias": 90,
    "Todo o feed": None,
}[period_label]
cutoff = (
    datetime.now(timezone.utc) - timedelta(days=period_days)
    if period_days is not None
    else None
)

filtered = []
for update in result.updates:
    searchable = f"{update.title} {update.summary} {update.source}".casefold()
    if query and query.casefold() not in searchable:
        continue
    if selected_area != "Todas" and update.area != selected_area:
        continue
    if selected_sources and update.source not in selected_sources:
        continue
    if cutoff is not None and update.published_at is not None:
        published = update.published_at
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        if published < cutoff:
            continue
    filtered.append(update)

st.markdown(f"### {len(filtered)} atualização(ões) encontrada(s)")
st.caption(
    "Os feeds são atualizados automaticamente e permanecem em cache por até "
    "30 minutos para preservar a estabilidade das fontes."
)

if not filtered:
    st.warning(
        "Nenhuma atualização corresponde aos filtros selecionados. "
        "Amplie o período ou limpe a pesquisa."
    )
else:
    for update in filtered[:40]:
        date_label = (
            update.published_at.astimezone().strftime("%d/%m/%Y")
            if update.published_at
            else "Data não informada"
        )
        render_update_card(
            titulo=update.title,
            resumo=update.summary,
            area=update.area,
            data_publicacao=date_label,
            fonte=update.source,
            url_fonte=update.source_url,
        )

st.markdown("## Portais oficiais para consulta direta")
st.caption(
    "Além dos feeds automáticos, estes portais devem ser consultados para "
    "confirmar vigência, íntegra, publicação e eventuais retificações."
)

for start in range(0, len(REFERENCE_PORTALS), 3):
    columns = st.columns(3, gap="medium")
    for column, (name, url, description) in zip(
        columns,
        REFERENCE_PORTALS[start : start + 3],
    ):
        with column:
            st.markdown(f"**{name}**")
            st.caption(description)
            st.link_button(
                "Abrir fonte oficial",
                url,
                use_container_width=True,
            )

st.html(
    """
    <div class="lex-note" style="margin-top:30px">
        <strong>Atenção:</strong> o título e o resumo servem para triagem.
        Para qualquer decisão profissional, confira a íntegra, a data de
        vigência, o órgão competente e possíveis alterações posteriores na
        fonte oficial.
    </div>
    """
)

render_footer()
