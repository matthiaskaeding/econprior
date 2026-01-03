# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx",
#     "econpriors",
# ]
#
# [tool.uv.sources]
# econpriors = { path = "..", editable = true }
# ///
"""Download articles from top economics journals."""

import argparse

from econpriors.get_data import db
from econpriors.get_data.fetch import fetch_journal_year
from econpriors.get_data.journals import JOURNALS


def main() -> None:
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
    parser.add_argument("--db", type=str, default="articles.db", help="Database path")
    args = parser.parse_args()

    conn = db.get_connection(args.db)
    db.init_db(conn)

    total = 0
    for journal in args.journals:
        for year in range(args.start_year, args.end_year + 1):
            print(f"Fetching {journal} {year} from {args.source}...")
            count = fetch_journal_year(journal, year, args.source, conn)
            print(f"  Added {count} new articles")
            total += count

    print(f"\nTotal: {total} new articles added")
    conn.close()


if __name__ == "__main__":
    main()
