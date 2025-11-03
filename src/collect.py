"""Collect news items from a curated set of RSS feeds.

This module replaces the original stub-based implementation with logic to
retrieve headlines and article summaries from a variety of news sources.
Each source is represented by one or more RSS feed URLs.  During
collection we parse the feeds using the feedparser library, convert
entries into ``NewsItem`` objects, and filter them so that only
stories published within the past ``n`` days are included.  The
resulting list of ``NewsItem`` instances is deduplicated by title
and source.

Note: RSS endpoints change over time.  The URLs provided below
represent typical entry points for each publication at the time
this module was authored.  If you notice missing headlines from a
particular source, update the corresponding feed list in
``RSS_FEEDS`` accordingly.
"""

from __future__ import annotations

import datetime as _dt
from typing import List, Dict, Iterable

import feedparser  # type: ignore

from .data_model import NewsItem


def get_time_window_days(days: int = 7) -> tuple[_dt.datetime, _dt.datetime]:
    """Return a UTC time window spanning the past ``days`` days.

    Parameters
    ----------
    days: int
        Number of days to look back from the current moment.

    Returns
    -------
    tuple[_dt.datetime, _dt.datetime]
        A tuple ``(start, end)`` representing the earliest and latest
        timestamps (both timezone-aware) used for filtering articles.
    """
    now = _dt.datetime.now(_dt.timezone.utc)
    start = now - _dt.timedelta(days=days)
    return start, now


# Mapping of source names to one or more RSS feed URLs.  You may
# customise this dictionary with additional feeds or replace the
# suggested endpoints with alternatives that better suit your needs.
RSS_FEEDS: Dict[str, Iterable[str]] = {
    # Jornais Diversos
    "Estadão": [
        "https://rss.estadao.com.br/saude",  # Saúde section (if available)
        "https://rss.estadao.com.br/ultimas",  # General news
    ],
    "Folha de S. Paulo": [
        "https://feeds.folha.uol.com.br/saude/rss091.xml",  # Health section
    ],
    "Valor Econômico": [
        # General economics and business news
        "https://valor.globo.com/rss/",  # Top stories
    ],
    "O Globo": [
        "https://oglobo.globo.com/rss.xml",  # Frontpage
    ],

    # Sites de negócios
    "Brazil Journal": [
        "https://braziljournal.com/feed/",  # General feed
    ],
    "NeoFeed": [
        "https://neofeed.com.br/feed/",  # All stories
    ],
    "Pipeline Valor": [
        "https://pipelinevalor.globo.com/feed/",  # Pipeline feed
    ],

    # Sites especializados
    "Medicina S/A": [
        "https://medicinasa.com.br/feed/",  # WordPress feed
    ],
    "Saúde Digital News": [
        "https://saudedigitalnews.com.br/feed/",  # WordPress feed
    ],
    "Healthcare": [
        # Placeholder for a specialised healthcare site; replace with
        # a specific feed URL for your preferred outlet.
        "https://www.healthcareitnews.com/homepage/feed",  # Example: Healthcare IT News
    ],

    # Outros Sites (internacionais)
    "Business Insider": [
        "https://www.businessinsider.com/rss/health",  # Health section feed
    ],
    "TechCrunch": [
        "https://techcrunch.com/feed/",  # TechCrunch global feed
    ],
    "Wall Street Journal": [
        "https://feeds.a.dj.com/rss/RSSWSJHealth.xml",  # Health & Science feed
    ],
    "New York Times": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",  # Health feed
    ],
}


def _parse_feed(source_name: str, url: str) -> List[NewsItem]:
    """Parse a single RSS feed and convert entries into NewsItems.

    Parameters
    ----------
    source_name: str
        Human-readable name of the source (e.g. 'Estadão').
    url: str
        The RSS feed URL to parse.

    Returns
    -------
    List[NewsItem]
        A list of NewsItem objects extracted from the feed.  If the
        feed cannot be parsed or contains no entries, an empty list is
        returned.
    """
    items: List[NewsItem] = []
    try:
        feed = feedparser.parse(url)
    except Exception:
        # If feedparser fails to fetch or parse, skip this feed
        return items

    # feed.entries may not exist if parsing failed
    for entry in getattr(feed, "entries", []):
        try:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            # Prefer 'summary' over 'description' when available
            summary = entry.get("summary", entry.get("description", "")).strip()

            # Determine publication date; fall back to now if missing
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                dt = _dt.datetime.fromtimestamp(
                    _dt.datetime(*entry.published_parsed[:6]).timestamp(),
                    tz=_dt.timezone.utc,
                )
            else:
                dt = _dt.datetime.now(_dt.timezone.utc)

            # Only consider entries with a non-empty title and link
            if not title or not link:
                continue

            items.append(
                NewsItem(
                    titulo=title,
                    fonte=source_name,
                    data_publicacao=dt,
                    url=link,
                    resumo_raw=summary,
                )
            )
        except Exception:
            # Skip malformed entries but continue processing others
            continue
    return items


def collect_all_sources(days: int = 7) -> List[NewsItem]:
    """Aggregate news items across all configured RSS feeds.

    This function iterates through each source and its associated feed
    URLs, parses them into NewsItems, filters them by date, and
    deduplicates the combined list.  Only articles published within
    the past ``days`` days (inclusive) are returned.

    Parameters
    ----------
    days: int, optional
        The number of days in the past to consider when filtering
        articles.  Defaults to 7.

    Returns
    -------
    List[NewsItem]
        A deduplicated list of NewsItem objects from the configured
        feeds.
    """
    start, end = get_time_window_days(days)
    collected: List[NewsItem] = []
    for source_name, feeds in RSS_FEEDS.items():
        for feed_url in feeds:
            for item in _parse_feed(source_name, feed_url):
                # Filter by publication time window
                if start <= item.data_publicacao <= end:
                    collected.append(item)

    # Deduplicate by (title, source) pair
    unique: Dict[tuple[str, str], NewsItem] = {}
    for item in collected:
        key = (item.titulo.strip().lower(), item.fonte.strip().lower())
        if key not in unique:
            unique[key] = item
    return list(unique.values())


if __name__ == "__main__":  # pragma: no cover
    # Allow manual testing by running this module directly.  It will
    # fetch recent articles from all sources and print a summary of the
    # number of items collected along with the first few titles.
    news_items = collect_all_sources(days=7)
    print(f"Coletadas {len(news_items)} notícias.")
    for item in news_items[:10]:
        print(f"- {item.fonte}: {item.titulo}")