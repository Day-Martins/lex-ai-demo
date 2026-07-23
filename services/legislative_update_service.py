from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class OfficialSource:
    name: str
    feed_url: str
    homepage_url: str
    default_area: str
    include_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class LegalUpdate:
    title: str
    summary: str
    source: str
    source_url: str
    published_at: datetime | None
    area: str


@dataclass(frozen=True)
class UpdateFetchResult:
    updates: list[LegalUpdate]
    unavailable_sources: list[str]


OFFICIAL_SOURCES = (
    OfficialSource(
        name="STJ — Notícias",
        feed_url="https://res.stj.jus.br/hrestp-c-portalp/RSS.xml",
        homepage_url="https://www.stj.jus.br/",
        default_area="Jurisprudência",
    ),
    OfficialSource(
        name="STJ — Informativo de Jurisprudência",
        feed_url=(
            "https://processo.stj.jus.br/jurisprudencia/externo/"
            "InformativoFeed"
        ),
        homepage_url="https://www.stj.jus.br/",
        default_area="Jurisprudência",
    ),
    OfficialSource(
        name="Câmara — Direito e Justiça",
        feed_url=(
            "https://www.camara.leg.br/noticias/rss/dinamico/"
            "DIREITO-E-JUSTICA"
        ),
        homepage_url="https://www.camara.leg.br/noticias/",
        default_area="Legislativo",
    ),
    OfficialSource(
        name="Câmara — Trabalho e Previdência",
        feed_url=(
            "https://www.camara.leg.br/noticias/rss/dinamico/"
            "TRABALHO-E-PREVIDENCIA"
        ),
        homepage_url="https://www.camara.leg.br/noticias/",
        default_area="Trabalhista e Previdenciário",
    ),
    OfficialSource(
        name="Senado Notícias",
        feed_url="https://www12.senado.leg.br/noticias/rss.xml",
        homepage_url="https://www12.senado.leg.br/noticias",
        default_area="Legislativo",
        include_keywords=(
            "lei",
            "projeto",
            "pl ",
            "pec",
            "código",
            "direito",
            "juríd",
            "regulament",
            "tribut",
            "trabalh",
            "consumidor",
            "previd",
        ),
    ),
    OfficialSource(
        name="Receita Federal",
        feed_url=(
            "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/rss.xml"
        ),
        homepage_url=(
            "https://www.gov.br/receitafederal/pt-br/assuntos/noticias"
        ),
        default_area="Tributário",
        include_keywords=(
            "tribut",
            "imposto",
            "fiscal",
            "contribuinte",
            "aduaneir",
            "declara",
            "cnpj",
            "parcelamento",
            "reforma",
            "arrecada",
        ),
    ),
)


REFERENCE_PORTALS = (
    (
        "Supremo Tribunal Federal",
        "https://portal.stf.jus.br/",
        "Jurisprudência constitucional e repercussão geral",
    ),
    (
        "Superior Tribunal de Justiça",
        "https://www.stj.jus.br/",
        "Jurisprudência federal infraconstitucional",
    ),
    (
        "Conselho Nacional de Justiça",
        "https://www.cnj.jus.br/agencia-cnj/",
        "Atos, políticas e notícias do Judiciário",
    ),
    (
        "Câmara dos Deputados",
        "https://www.camara.leg.br/noticias/",
        "Projetos e atividade legislativa",
    ),
    (
        "Senado Federal",
        "https://www12.senado.leg.br/noticias",
        "Projetos, votações e novas leis",
    ),
    (
        "Diário Oficial da União",
        "https://www.in.gov.br/",
        "Publicação oficial de leis e atos normativos",
    ),
    (
        "Receita Federal",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias",
        "Normas e orientações tributárias",
    ),
)


AREA_KEYWORDS = (
    (
        "Tributário",
        (
            "tribut",
            "imposto",
            "fiscal",
            "receita federal",
            "ibs",
            "cbs",
            "icms",
            "iss",
            "contribuinte",
        ),
    ),
    (
        "Trabalhista e Previdenciário",
        (
            "trabalh",
            "emprego",
            "empregado",
            "previd",
            "inss",
            "aposent",
        ),
    ),
    (
        "Civil e Consumidor",
        (
            "civil",
            "consumidor",
            "contrato",
            "família",
            "sucess",
            "indeniza",
            "responsabilidade",
        ),
    ),
    (
        "Penal",
        (
            "penal",
            "crime",
            "criminal",
            "prisão",
            "réu",
            "execução penal",
        ),
    ),
    (
        "Constitucional e Administrativo",
        (
            "constitucional",
            "administra",
            "servidor",
            "licitação",
            "improbidade",
            "política pública",
        ),
    ),
    (
        "Digital e Proteção de Dados",
        (
            "digital",
            "internet",
            "dados pessoais",
            "lgpd",
            "inteligência artificial",
            "plataforma",
        ),
    ),
)


def _strip_markup(value: str | None) -> str:
    if not value:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", value)
    normalized = re.sub(r"\s+", " ", html.unescape(without_tags))
    normalized = re.sub(r"\s+([.,;:!?])", r"\1", normalized)
    return normalized.strip()


def _find_text(element: ET.Element, names: Iterable[str]) -> str:
    for name in names:
        found = element.find(name)
        if found is not None and found.text:
            return found.text.strip()

    wanted = {name.split("}")[-1].lower() for name in names}
    for child in element:
        if child.tag.split("}")[-1].lower() in wanted and child.text:
            return child.text.strip()
    return ""


def _extract_link(element: ET.Element) -> str:
    direct = _find_text(element, ("link",))
    if direct:
        return direct
    for child in element:
        if child.tag.split("}")[-1].lower() == "link":
            href = child.attrib.get("href", "").strip()
            if href:
                return href
    return ""


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError, OverflowError):
        pass

    iso_value = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso_value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def classify_area(title: str, summary: str, default_area: str) -> str:
    content = f"{title} {summary}".lower()
    for area, keywords in AREA_KEYWORDS:
        if any(keyword in content for keyword in keywords):
            return area
    return default_area


def _safe_official_url(url: str, source: OfficialSource) -> str:
    parsed = urlparse(url)
    source_host = urlparse(source.homepage_url).hostname or ""
    candidate_host = parsed.hostname or ""
    source_base = source_host.removeprefix("www.")
    if (
        parsed.scheme in {"http", "https"}
        and candidate_host
        and (
            candidate_host == source_base
            or candidate_host.endswith(f".{source_base}")
        )
    ):
        return url
    return source.homepage_url


def parse_feed(xml_content: bytes, source: OfficialSource) -> list[LegalUpdate]:
    root = ET.fromstring(xml_content)
    entries = [
        element
        for element in root.iter()
        if element.tag.split("}")[-1].lower() in {"item", "entry"}
    ]

    updates: list[LegalUpdate] = []
    for entry in entries:
        title = _strip_markup(_find_text(entry, ("title",)))
        if not title:
            continue

        summary = _strip_markup(
            _find_text(
                entry,
                ("description", "summary", "content", "encoded"),
            )
        )
        combined_content = f"{title} {summary}".casefold()
        if source.include_keywords and not any(
            keyword in combined_content
            for keyword in source.include_keywords
        ):
            continue
        if len(summary) > 500:
            summary = f"{summary[:497].rstrip()}..."
        published = _parse_date(
            _find_text(
                entry,
                ("pubDate", "published", "updated", "date"),
            )
        )
        link = _safe_official_url(_extract_link(entry), source)
        area = classify_area(title, summary, source.default_area)
        updates.append(
            LegalUpdate(
                title=title,
                summary=summary or "Consulte a fonte oficial para os detalhes.",
                source=source.name,
                source_url=link,
                published_at=published,
                area=area,
            )
        )
    return updates


def fetch_legal_updates(
    *,
    per_source: int = 12,
    timeout_seconds: int = 8,
) -> UpdateFetchResult:
    collected: list[LegalUpdate] = []
    unavailable: list[str] = []
    headers = {
        "User-Agent": (
            "LEX-AI-Legal-Updates/1.0 "
            "(consulta de fontes oficiais; contato via plataforma)"
        )
    }

    def fetch_source(
        source: OfficialSource,
    ) -> tuple[list[LegalUpdate], str | None]:
        try:
            response = requests.get(
                source.feed_url,
                headers=headers,
                timeout=timeout_seconds,
            )
            response.raise_for_status()
            updates = parse_feed(response.content, source)
            return updates[:per_source], None
        except (requests.RequestException, ET.ParseError, ValueError):
            return [], source.name

    with ThreadPoolExecutor(max_workers=len(OFFICIAL_SOURCES)) as executor:
        source_results = executor.map(fetch_source, OFFICIAL_SOURCES)
        for updates, unavailable_source in source_results:
            collected.extend(updates)
            if unavailable_source:
                unavailable.append(unavailable_source)

    unique: dict[tuple[str, str], LegalUpdate] = {}
    for update in collected:
        unique[(update.title.casefold(), update.source_url)] = update

    ordered = sorted(
        unique.values(),
        key=lambda item: item.published_at or datetime.min.replace(
            tzinfo=timezone.utc
        ),
        reverse=True,
    )
    return UpdateFetchResult(ordered, unavailable)
