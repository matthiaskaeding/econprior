import time
from collections.abc import Iterator
from typing import Any

import httpx


def fetch_journal_works(
    issn: str,
    year: int,
    per_page: int = 100,
    base_url: str = "https://api.openalex.org",
    mailto: str = "econprior@example.com",
) -> Iterator[dict[str, Any]]:
    """Fetch all works from a journal for a given year."""
    url = f"{base_url}/works"
    params = {
        "filter": f"primary_location.source.issn:{issn},publication_year:{year}",
        "per_page": per_page,
        "cursor": "*",
        "mailto": mailto,
    }

    with httpx.Client(timeout=30.0) as client:
        while True:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                break

            yield from results

            next_cursor = data.get("meta", {}).get("next_cursor")
            if not next_cursor:
                break

            params["cursor"] = next_cursor
            time.sleep(0.1)  # polite delay


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return None

    words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words.append((pos, word))

    words.sort(key=lambda x: x[0])
    return " ".join(word for _, word in words)


def parse_article(item: dict[str, Any]) -> dict[str, Any] | None:
    """Parse an OpenAlex work item into article format."""
    doi = item.get("doi")
    if doi:
        doi = doi.replace("https://doi.org/", "")
    else:
        return None

    title = item.get("title")
    abstract = reconstruct_abstract(item.get("abstract_inverted_index"))

    authors = []
    for authorship in item.get("authorships", []):
        author = authorship.get("author", {})
        if name := author.get("display_name"):
            authors.append(name)

    year = item.get("publication_year")

    location = item.get("primary_location", {}) or {}
    source = location.get("source", {}) or {}
    journal = source.get("display_name")

    return {
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "year": year,
        "journal": journal,
    }
