import sqlite3

from econpriors.get_data import db
from econpriors.get_data.apis import crossref, openalex
from econpriors.get_data.journals import get_issn, get_name


def fetch_journal_year(
    journal: str,
    year: int,
    source: str,
    conn: sqlite3.Connection,
    max_articles: int | None = None,
) -> int:
    """
    Fetch all articles for a journal/year from specified source.

    Args:
        journal: Journal key (e.g., 'aer', 'qje')
        year: Publication year
        source: Data source ('crossref' or 'openalex')
        conn: SQLite connection
        max_articles: Maximum number of articles to fetch (None for unlimited)

    Returns:
        Count of new articles added
    """
    issn = get_issn(journal)
    journal_name = get_name(journal)
    existing_dois = db.get_existing_dois(conn, journal_name, year)

    if source == "crossref":
        api_module = crossref
    elif source == "openalex":
        api_module = openalex
    else:
        raise ValueError(f"Unknown source: {source}")

    count = 0
    for item in api_module.fetch_journal_works(issn, year):
        if max_articles is not None and count >= max_articles:
            break

        article = api_module.parse_article(item)
        if article is None:
            continue

        doi = article["doi"]
        if doi in existing_dois:
            continue

        db.insert_article(
            conn,
            doi=doi,
            title=article["title"],
            abstract=article["abstract"],
            journal=journal_name,
            year=article["year"] or year,
            authors=article["authors"],
            source=source,
        )
        count += 1

    conn.commit()
    return count
