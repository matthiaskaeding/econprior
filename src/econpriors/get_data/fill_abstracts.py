import logging
import sqlite3
from collections.abc import Callable, Iterable
from typing import Any

import httpx

from econpriors.get_data.apis import openalex

MAILTO = "econpriors@example.com"

logger = logging.getLogger(__name__)

Article = dict[str, Any]
ProgressCallback = Callable[[Article, str, bool], None]


def get_articles_missing_abstract(conn: sqlite3.Connection) -> list[Article]:
    """Get all articles that do not yet have an abstract."""
    cursor = conn.execute("SELECT id, doi, source FROM articles WHERE abstract IS NULL")
    rows = cursor.fetchall()
    return [
        {"id": row[0], "doi": row[1], "source": row[2]}
        for row in rows
        if row[1]  # ignore malformed rows lacking a DOI
    ]


def fetch_abstract_from_openalex(doi: str) -> str | None:
    """Try to fetch abstract from OpenAlex for a given DOI."""
    url = f"https://api.openalex.org/works/doi:{doi}"
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params={"mailto": MAILTO})
            response.raise_for_status()
            data = response.json()
            inverted_index = data.get("abstract_inverted_index")
            return openalex.reconstruct_abstract(inverted_index)
    except httpx.HTTPError as exc:
        logger.warning("OpenAlex request failed for %s: %s", doi, exc)
        return None


def fetch_abstract_from_crossref(doi: str) -> str | None:
    """Try to fetch abstract from Crossref for a given DOI."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params={"mailto": MAILTO})
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("abstract")
    except httpx.HTTPError as exc:
        logger.warning("Crossref request failed for %s: %s", doi, exc)
        return None


def update_abstract(conn: sqlite3.Connection, article_id: int, abstract: str) -> None:
    """Update an article's abstract in the database."""
    conn.execute(
        "UPDATE articles SET abstract = ? WHERE id = ?",
        (abstract, article_id),
    )


def fill_missing_abstracts(
    conn: sqlite3.Connection,
    articles: Iterable[Article] | None = None,
    progress_callback: ProgressCallback | None = None,
) -> int:
    """
    Try to fill missing abstracts from alternative sources.

    Returns the number of abstracts updated.
    """
    if articles is None:
        articles = get_articles_missing_abstract(conn)

    filled = 0

    for article in articles:
        doi = article.get("doi")
        source = article.get("source")

        # Skip malformed rows early.
        if not doi or not source:
            if progress_callback:
                progress_callback(article, "unknown", False)
            continue

        target_source = "openalex" if source == "crossref" else "crossref"
        if target_source == "openalex":
            abstract = fetch_abstract_from_openalex(doi)
        else:
            abstract = fetch_abstract_from_crossref(doi)

        success = bool(abstract)
        if success and abstract:
            update_abstract(conn, article["id"], abstract)
            filled += 1

        if progress_callback:
            progress_callback(article, target_source, success)

    conn.commit()
    return filled
