"""Download articles from top economics journals."""

from __future__ import annotations

import argparse
from pathlib import Path

from tqdm import tqdm

from econprior.get_data import db
from econprior.get_data.fetch import fetch_journal_year
from econprior.get_data.journals import JOURNALS


def main() -> None:
    """CLI entry point for downloading article metadata."""

    parser = argparse.ArgumentParser(description="Download journal articles")
    parser.add_argument(
        "--start-year", type=int, default=2020, help="Start year (inclusive)"
    )
    parser.add_argument(
        "--end-year", type=int, default=2025, help="End year (inclusive)"
    )
    parser.add_argument(
        "--source",
        choices=["crossref", "openalex"],
        default="openalex",
        help="Data source",
    )
    parser.add_argument(
        "--journals",
        nargs="+",
        choices=list(JOURNALS.keys()),
        default=list(JOURNALS.keys()),
        help="Journals to fetch",
    )
    parser.add_argument(
        "--db", type=str, default="data/articles.db", help="Database path"
    )
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    conn = db.get_connection(db_path)
    db.init_db(conn)

    tasks = [
        (journal, year)
        for journal in args.journals
        for year in range(args.start_year, args.end_year + 1)
    ]

    total = 0
    for journal, year in tqdm(tasks, desc=f"Fetching from {args.source}"):
        count = fetch_journal_year(journal, year, args.source, conn)
        total += count

    print(f"\nTotal: {total} new articles added")
    conn.close()


if __name__ == "__main__":
    main()
