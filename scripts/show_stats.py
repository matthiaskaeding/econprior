# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "polars",
#     "connectorx",
#     "pyarrow",
#     "econpriors",
# ]
#
# [tool.uv.sources]
# econpriors = { path = "..", editable = true }
# ///
"""Show statistics about downloaded articles."""

import argparse

import polars as pl


def main() -> None:
    parser = argparse.ArgumentParser(description="Show article statistics")
    parser.add_argument("--db", type=str, default="articles.db", help="Database path")
    args = parser.parse_args()

    df = pl.read_database_uri(
        "SELECT * FROM articles",
        f"sqlite://{args.db}",
    )

    print("=" * 60)
    print("ARTICLES DATABASE OVERVIEW")
    print("=" * 60)
    print(f"\nTotal articles: {len(df)}")
    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nColumns: {df.columns}")

    print("\n" + "-" * 60)
    print("SAMPLE DATA (first 5 rows)")
    print("-" * 60)
    print(df.head())

    print("\n" + "-" * 60)
    print("ARTICLES BY JOURNAL")
    print("-" * 60)
    by_journal = df.group_by("journal").len().sort("len", descending=True)
    print(by_journal)

    print("\n" + "-" * 60)
    print("ARTICLES BY YEAR")
    print("-" * 60)
    by_year = df.group_by("year").len().sort("year")
    print(by_year)

    print("\n" + "-" * 60)
    print("ARTICLES BY SOURCE")
    print("-" * 60)
    by_source = df.group_by("source").len().sort("len", descending=True)
    print(by_source)

    print("\n" + "-" * 60)
    print("ABSTRACT COVERAGE")
    print("-" * 60)
    has_abstract = df.filter(pl.col("abstract").is_not_null()).height
    print(f"With abstract: {has_abstract} ({100 * has_abstract / len(df):.1f}%)")
    print(f"Without abstract: {len(df) - has_abstract}")


if __name__ == "__main__":
    main()
