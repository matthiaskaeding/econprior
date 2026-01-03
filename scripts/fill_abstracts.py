# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx",
#     "tqdm",
#     "econpriors",
# ]
#
# [tool.uv.sources]
# econpriors = { path = "..", editable = true }
# ///
"""Fill missing abstracts from alternative sources."""

import argparse
from pathlib import Path

from tqdm import tqdm

from econpriors.get_data import db
from econpriors.get_data.fill_abstracts import (
    fetch_abstract_from_crossref,
    fetch_abstract_from_openalex,
    get_articles_missing_abstract,
    update_abstract,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing abstracts")
    parser.add_argument(
        "--db", type=str, default="data/articles.db", help="Database path"
    )
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    conn = db.get_connection(db_path)

    missing = get_articles_missing_abstract(conn)
    print(f"Found {len(missing)} articles with missing abstracts")

    filled = 0
    for article in tqdm(missing, desc="Filling abstracts"):
        doi = article["doi"]
        source = article["source"]

        if source == "crossref":
            abstract = fetch_abstract_from_openalex(doi)
        else:
            abstract = fetch_abstract_from_crossref(doi)

        if abstract:
            update_abstract(conn, article["id"], abstract)
            filled += 1

    conn.commit()
    print(f"\nFilled {filled} abstracts")
    conn.close()


if __name__ == "__main__":
    main()
