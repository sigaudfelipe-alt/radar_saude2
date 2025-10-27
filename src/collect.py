"""Collect news items from various sources.

This module defines functions for scraping or querying news sources for
relevant articles about the healthcare sector. For the purposes of this
template, simple stub functions are provided. You should replace these
stubs with real implementations that fetch articles from the desired
sources (Valor Econômico, Folha de São Paulo, TechCrunch, etc.).

Each stub returns a list of `NewsItem` instances that share a common
interface expected by the rest of the pipeline.
"""

import requests  # type: ignore  # For real fetches; not used in stubs.
from datetime import datetime, timedelta, timezone
from typing import List

from .data_model import NewsItem


# Define a list of keywords relevant to the healthcare newsletter. These
# keywords help narrow down searches when querying external APIs or feeds.
KEYWORDS = [
    "plano de saúde",
    "operadora de saúde",
    "telemedicina",
    "healthtech",
    "aquisição",
    "Conexa Saúde",
    "coordenação de cuidado",
    "ans saúde",
    "custo assistencial",
    "atenção primária",
    "oncologia"
]


def get_time_window_days(days: int = 7) -> tuple[datetime, datetime]:
    """Return the datetime window representing the past `days` days."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    return start, now


def fetch_stub_valor(keyword: str) -> List[NewsItem]:
    """Stub for fetching news from Valor Econômico.

    In a real implementation, this function would query the Valor
    Econômico site or API for articles containing `keyword`. As a
    placeholder, it returns a single NewsItem with dummy content.
    """
    now = datetime.now(timezone.utc)
    return [
        NewsItem(
            titulo=f"Exemplo Valor: {keyword} impacta operadoras",
            fonte="Valor Econômico",
            data_publicacao=now,
            url="https://valor-ficticio.com/exemplo",
            resumo_raw=(
                f"O {keyword} está gerando pressão de custo e empurrando operadoras a rever modelo assistencial."
            ),
        )
    ]


def fetch_stub_techcrunch(keyword: str) -> List[NewsItem]:
    """Stub for fetching news from TechCrunch.

    As above, this stub returns a static NewsItem describing a sample
    funding round or technology investment.
    """
    now = datetime.now(timezone.utc)
    return [
        NewsItem(
            titulo=(
                f"Startup de {keyword} levanta rodada Série A focada em coordenação de cuidado"
            ),
            fonte="TechCrunch",
            data_publicacao=now,
            url="https://techcrunch-ficticio.com/deal",
            resumo_raw=(
                "A rodada mira expansão de uma plataforma digital de triagem e acompanhamento remoto de crônicos."
            ),
        )
    ]


def collect_all_sources() -> List[NewsItem]:
    """Aggregate news items across all sources and keywords.

    This function iterates through all keywords, calls the stub fetch
    functions for each source, deduplicates the results, and returns a
    consolidated list of news items. Replace the calls here with real
    fetches when implementing your production collector.
    """
    # Determine the relevant time window (unused by stubs but useful later).
    get_time_window_days(7)

    collected: List[NewsItem] = []
    for kw in KEYWORDS:
        collected.extend(fetch_stub_valor(kw))
        collected.extend(fetch_stub_techcrunch(kw))

    # Deduplicate by (title, source) pair to avoid repeated items.
    unique_items: dict[tuple[str, str], NewsItem] = {}
    for item in collected:
        key = (item.titulo.strip().lower(), item.fonte.strip().lower())
        if key not in unique_items:
            unique_items[key] = item
    return list(unique_items.values())


if __name__ == "__main__":
    # Simple test to ensure collection returns unique stubs.
    items = collect_all_sources()
    print(f"Coletadas {len(items)} notícias.")
    for i in items[:5]:
        print(i)