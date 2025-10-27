"""Classify news items and generate executive summaries using an LLM.

This module contains functions that take a list of NewsItem objects,
determine which section of the newsletter each belongs to, and produce
short summaries explaining why each article is important. The module
integrates with the OpenAI API to generate these summaries. If no API
key is provided, the code falls back to rule-based heuristics similar
to the initial MVP.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import openai  # type: ignore  # The user must install this package.

from .data_model import NewsItem, DealItem, WeeklyNewsletter


def classify_section(item: NewsItem) -> str:
    """Categorize a NewsItem into a section based on keywords and source.

    The classification rules are intentionally simple. They rely on
    keywords found in the title and raw summary, and use the source to
    differentiate between Brazilian and international coverage.
    """
    text = (item.titulo + " " + item.resumo_raw).lower()

    if "conexa" in text:
        return "conexa"

    if any(k in text for k in ["aquisição", "adquiriu", "rodada", "série a", "investimento"]):
        return "deal"

    if any(k in text for k in ["telemedicina", "coordenação de cuidado", "atenção primária", "cuidado integrado"]):
        return "saude_digital"

    if any(k in text for k in ["ia", "inteligência artificial", "plataforma digital", "dispositivo", "wearable"]):
        return "tech_saude"

    br_sources = [
        "valor econômico",
        "folha",
        "o globo",
        "estadão",
        "neofeed",
        "brazil journal",
        "pipeline valor",
        "saúde digital news",
        "medicina s/a",
    ]
    if item.fonte.strip().lower() in br_sources:
        return "panorama_brasil"
    return "panorama_global"


def summarize_with_llm(title: str, excerpt: str) -> str:
    """Generate a brief executive summary using an LLM via OpenAI API.

    The function constructs a prompt combining the title and excerpt
    and requests the assistant to produce one or two sentences explaining
    why this news matters for the healthcare sector. If the OpenAI API
    is not available (e.g., missing API key), it returns a fallback
    summary based on simple keyword heuristics.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback if no API key is provided.
        text = (title + " " + excerpt).lower()
        if "custo" in text or "sinistro" in text or "sinistralidade" in text:
            return "Pressiona custo assistencial e força operadoras a rever modelo de cuidado."
        if any(k in text for k in ["telemedicina", "coordenação de cuidado"]):
            return "Mostra avanço de modelos digitais e coordenação de cuidado para reduzir urgência e sinistro."
        if any(k in text for k in ["rodada", "investimento", "série a"]):
            return "Sinaliza onde investidores acreditam que está o próximo motor de crescimento em saúde digital."
        if any(k in text for k in ["aquisição", "adquiriu"]):
            return "Movimento de consolidação e verticalização do cuidado."
        return "Indica mudança estrutural no modelo de saúde e potencial impacto financeiro/regulatório."

    # Configure OpenAI client.
    openai.api_key = api_key
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    prompt = (
        "Você é um assistente analista que escreve resumidamente sobre o setor "
        "de saúde. A seguir, um título de notícia e um trecho inicial. Em no máximo "
        "duas frases, explique por que essa notícia é relevante para o mercado de saúde "
        "suplementar e quais tendências ou riscos ela evidencia."
    )

    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": f"Título: {title}\nTrecho: {excerpt}\nResposta em duas frases:",
        },
    ]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=60,
            temperature=0.4,
        )
        summary = response.choices[0].message["content"].strip()
        return summary
    except Exception as e:
        # On failure, fall back to the rule-based summaries.
        text = (title + " " + excerpt).lower()
        if "custo" in text or "sinistro" in text or "sinistralidade" in text:
            return "Pressiona custo assistencial e força operadoras a rever modelo de cuidado."
        if any(k in text for k in ["telemedicina", "coordenação de cuidado"]):
            return "Mostra avanço de modelos digitais e coordenação de cuidado para reduzir urgência e sinistro."
        if any(k in text for k in ["rodada", "investimento", "série a"]):
            return "Sinaliza onde investidores acreditam que está o próximo motor de crescimento em saúde digital."
        if any(k in text for k in ["aquisição", "adquiriu"]):
            return "Movimento de consolidação e verticalização do cuidado."
        return "Indica mudança estrutural no modelo de saúde e potencial impacto financeiro/regulatório."


def split_sections(news_list: List[NewsItem]) -> tuple[
    List[NewsItem], List[NewsItem], List[NewsItem], List[NewsItem], List[NewsItem], List[NewsItem]
]:
    """Separate the news items into their respective sections.

    Returns six lists, corresponding to each section type in the following
    order: panorama_brasil, panorama_global, saude_digital, tech_saude,
    deal, conexa.
    """
    panorama_brasil = []
    panorama_global = []
    saude_digital = []
    tech_saude = []
    deals = []
    conexa = []

    for item in news_list:
        sec = classify_section(item)
        item.secao = sec  # annotate the item
        # Always generate the executive summary using the LLM (or fallback)
        item.resumo_exec = summarize_with_llm(item.titulo, item.resumo_raw)

        if sec == "panorama_brasil":
            panorama_brasil.append(item)
        elif sec == "panorama_global":
            panorama_global.append(item)
        elif sec == "saude_digital":
            saude_digital.append(item)
        elif sec == "tech_saude":
            tech_saude.append(item)
        elif sec == "deal":
            deals.append(item)
        elif sec == "conexa":
            conexa.append(item)

    return (
        panorama_brasil,
        panorama_global,
        saude_digital,
        tech_saude,
        deals,
        conexa,
    )


def extract_deals(deals_news: List[NewsItem]) -> tuple[List[DealItem], List[DealItem]]:
    """Convert news items tagged as deals into DealItem structures.

    Without sophisticated NER, the fields are left generic. A more
    advanced implementation could parse the titles for company names and
    valuations using regex or the LLM.
    """
    brasil_deals: List[DealItem] = []
    global_deals: List[DealItem] = []

    for n in deals_news:
        deal = DealItem(
            alvo="Alvo não mapeado",
            comprador_investidor="Investidor não mapeado",
            valor="não divulgado",
            tese=n.resumo_exec or "",
            contexto="Brasil/Latam",
        )

        src = n.fonte.lower()
        if src in ["techcrunch", "wall street journal", "new york times", "financial times"]:
            deal.contexto = "Global"

        if deal.contexto == "Global":
            global_deals.append(deal)
        else:
            brasil_deals.append(deal)

    return brasil_deals, global_deals


def build_weekly_newsletter(news_list: List[NewsItem]) -> WeeklyNewsletter:
    """Assemble a WeeklyNewsletter object from a list of NewsItems.

    This function orchestrates the section splitting, deal extraction, and
    construction of the final `WeeklyNewsletter` data structure. It also
    constructs default bullets, agenda items, and a closing paragraph.
    """
    # Organize items into sections
    (
        pan_br,
        pan_gl,
        sdigital,
        stech,
        deals_news,
        conexa_news,
    ) = split_sections(news_list)
    deals_br, deals_gl = extract_deals(deals_news)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    periodo_label = f"Semana de {start.strftime('%d/%m/%Y')} a {now.strftime('%d/%m/%Y')}"

    bullets: List[str] = []
    # Top bullets: pick the first items from sections if available
    if pan_br:
        bullets.append(f"{pan_br[0].titulo} – {pan_br[0].resumo_exec}")
    if sdigital:
        bullets.append(f"{sdigital[0].titulo} – {sdigital[0].resumo_exec}")
    if deals_news:
        bullets.append(
            "Deals em saúde: consolidação e capital entrando em coordenação de cuidado."
        )

    conexa_blocos: List[str] = []
    if conexa_news:
        for c in conexa_news[:2]:
            conexa_blocos.append(
                f"{c.titulo} ({c.fonte})\n- {c.resumo_exec}\n- Link: {c.url}"
            )
    else:
        conexa_blocos.append(
            "Conexa em destaque esta semana: [preencher manualmente desempenho, novos contratos, indicadores de resolutividade, participação em eventos]."
        )

    agenda = [
        "Próxima semana: acompanhar movimentação regulatória da ANS sobre custo assistencial e telemedicina.",
        "Eventos setoriais: acompanhar debates de atenção primária corporativa e coordenação de cuidado.",
    ]

    fechamento = (
        "Custos assistenciais continuam pressionando operadoras e empregadores. "
        "Modelos digitais de coordenação de cuidado e pronto atendimento virtual "
        "estão migrando de promessa para estratégia financeira."
    )

    return WeeklyNewsletter(
        periodo_label=periodo_label,
        bullets_top3=bullets,
        panorama_brasil=pan_br[:5],
        panorama_global=pan_gl[:5],
        saude_digital=sdigital[:5],
        tech_saude=stech[:5],
        deals_brasil=deals_br[:5],
        deals_global=deals_gl[:5],
        conexa_blocos=conexa_blocos,
        agenda_itens=agenda,
        fechamento=fechamento,
    )


if __name__ == "__main__":
    # Quick test to build a newsletter with stub data
    from .collect import collect_all_sources

    items = collect_all_sources()
    newsletter = build_weekly_newsletter(items)
    print(newsletter)