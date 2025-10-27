from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Optional

# Define literal types for the different sections of the newsletter.
SectionType = Literal[
    "panorama_brasil",
    "panorama_global",
    "saude_digital",
    "tech_saude",
    "deal",
    "conexa"
]


@dataclass
class NewsItem:
    """Represents a single news article captured during collection."""
    titulo: str
    fonte: str
    data_publicacao: datetime
    url: str
    resumo_raw: str  # Raw excerpt or first paragraph extracted from the source.
    secao: Optional[SectionType] = None
    resumo_exec: Optional[str] = None  # A brief executive summary (why it matters)


@dataclass
class DealItem:
    """Represents a deal (M&A, investment, etc.) for the newsletter."""
    alvo: str
    comprador_investidor: str
    valor: str  # Could be "não divulgado" if unknown.
    tese: str
    contexto: str  # Either "Brasil/Latam" or "Global"


@dataclass
class WeeklyNewsletter:
    """Aggregated structure for a single weekly newsletter edition."""
    periodo_label: str  # e.g. "Semana de 20/10/2025 a 27/10/2025"
    bullets_top3: List[str]
    panorama_brasil: List[NewsItem]
    panorama_global: List[NewsItem]
    saude_digital: List[NewsItem]
    tech_saude: List[NewsItem]
    deals_brasil: List[DealItem]
    deals_global: List[DealItem]
    conexa_blocos: List[str]
    agenda_itens: List[str]
    fechamento: str