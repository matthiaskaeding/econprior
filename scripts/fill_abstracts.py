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
    fill_missing_abstracts,
    get_articles_missing_abstract,
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

    if not missing:
        conn.close()
        return

    with tqdm(total=len(missing), desc="Filling abstracts") as progress:

        def on_progress(article: dict, target_source: str, success: bool) -> None:
            progress.update()
            progress.set_postfix(
                {"source": target_source, "status": "filled" if success else "miss"}
            )

        filled = fill_missing_abstracts(
            conn, articles=missing, progress_callback=on_progress
        )

    print(f"\nFilled {filled} abstracts")
    conn.close()


if __name__ == "__main__":
    main()
