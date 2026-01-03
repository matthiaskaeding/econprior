import time
from collections.abc import Iterator
from typing import Any

import httpx


def fetch_journal_works(
    issn: str,
    year: int,
    per_page: int = 100,
    base_url: str = "https://api.crossref.org",
    mailto: str = "econpriors@example.com",
) -> Iterator[dict[str, Any]]:
    """Fetch all works from a journal for a given year."""
    url = f"{base_url}/journals/{issn}/works"
    params = {
        "filter": f"from-pub-date:{year},until-pub-date:{year}",
        "rows": per_page,
        "cursor": "*",
        "mailto": mailto,
    }

    with httpx.Client(timeout=30.0) as client:
        while True:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data["message"]["items"]
            if not items:
                break

            yield from items

            next_cursor = data["message"].get("next-cursor")
            if not next_cursor or next_cursor == params["cursor"]:
                break

            params["cursor"] = next_cursor
            time.sleep(0.1)  # polite delay


def parse_article(item: dict[str, Any]) -> dict[str, Any] | None:
    """Parse a Crossref work item into article format."""
    doi = item.get("DOI")
    if not doi:
        return None

    title_list = item.get("title", [])
    title = title_list[0] if title_list else None

    abstract = item.get("abstract")

    authors = []
    for author in item.get("author", []):
        name_parts = []
        if given := author.get("given"):
            name_parts.append(given)
        if family := author.get("family"):
            name_parts.append(family)
        if name_parts:
            authors.append(" ".join(name_parts))

    published = item.get("published", {}).get("date-parts", [[None]])[0]
    year = published[0] if published else None

    container = item.get("container-title", [])
    journal = container[0] if container else None

    return {
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "year": year,
        "journal": journal,
    }
