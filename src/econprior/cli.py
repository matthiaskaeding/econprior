"""Typer-based CLI for econprior utility scripts."""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Literal, Optional

import polars as pl
import typer
from tqdm import tqdm

from econprior.get_data import db
from econprior.get_data.fetch import fetch_journal_year
from econprior.get_data.fill_abstracts import (
    fill_missing_abstracts,
    get_articles_missing_abstract,
)
from econprior.get_data.journals import JOURNALS


app = typer.Typer(
    help="CLI entry point for econprior scripting utilities.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _resolve_db(path: Path) -> Path:
    return path.expanduser().resolve()


SourceOption = Literal["crossref", "openalex"]


@app.command()
def download(
    start_year: int = typer.Option(2020, help="Start year (inclusive)"),
    end_year: int = typer.Option(2025, help="End year (inclusive)"),
    source: SourceOption = typer.Option("openalex", help="Source to fetch articles"),
    journals: Optional[str] = typer.Option(
        None, "--journals", help="Comma-separated journal codes (all by default)"
    ),
    db_path: Path = typer.Option(
        Path("data/articles.db"), "--db", help="Path to the SQLite database"
    ),
) -> None:
    """Download article metadata into the local SQLite database."""

    if start_year > end_year:
        raise typer.BadParameter("start-year must be <= end-year")

    if journals:
        selected_journals = [j.strip() for j in journals.split(",") if j.strip()]
    else:
        selected_journals = list(JOURNALS.keys())
    missing = sorted(set(selected_journals) - set(JOURNALS.keys()))
    if missing:
        raise typer.BadParameter(f"Unknown journals: {', '.join(missing)}")

    resolved_db = _resolve_db(db_path)
    conn = db.get_connection(resolved_db)
    db.init_db(conn)

    try:
        tasks = list(
            itertools.product(selected_journals, range(start_year, end_year + 1))
        )
        total = 0
        with tqdm(tasks, desc=f"Fetching from {source}") as iterator:
            for journal, year in iterator:
                count = fetch_journal_year(journal, year, source, conn)
                total += count
                iterator.set_postfix({"journal": journal, "year": year})
    finally:
        conn.close()

    typer.echo(f"Total: {total} new articles added")


@app.command()
def fill(
    db_path: Path = typer.Option(
        Path("data/articles.db"), "--db", help="Path to the SQLite database"
    ),
) -> None:
    """Fill missing abstracts using the opposite source."""

    resolved_db = _resolve_db(db_path)
    conn = db.get_connection(resolved_db)

    try:
        missing = get_articles_missing_abstract(conn)
        typer.echo(f"Found {len(missing)} articles with missing abstracts")

        if not missing:
            return

        with tqdm(total=len(missing), desc="Filling abstracts") as progress:

            def on_progress(article: dict, target_source: str, success: bool) -> None:
                progress.update()
                progress.set_postfix(
                    {
                        "source": target_source,
                        "status": "filled" if success else "miss",
                    }
                )

            filled = fill_missing_abstracts(
                conn, articles=missing, progress_callback=on_progress
            )
        typer.echo(f"Filled {filled} abstracts")
    finally:
        conn.close()


@app.command()
def stats(
    db_path: Path = typer.Option(
        Path("data/articles.db"), "--db", help="Path to the SQLite database"
    ),
    sample_rows: int = typer.Option(5, help="Number of sample rows to display"),
) -> None:
    """Print summary statistics about the stored articles."""

    resolved_db = _resolve_db(db_path)
    conn_uri = f"sqlite:///{resolved_db.as_posix()}"
    typer.echo(f"Reading articles from {conn_uri}")

    df = pl.read_database_uri("SELECT * FROM articles", conn_uri)
    typer.echo(f"Loaded {len(df)} articles")

    summary = pl.DataFrame(
        {
            "metric": ["Total articles", "DataFrame shape", "Columns"],
            "value": [
                str(len(df)),
                f"{df.shape[0]} rows x {df.shape[1]} cols",
                ", ".join(df.columns),
            ],
        }
    )
    typer.echo(summary)

    typer.echo("\nSample data")
    typer.echo(df.head(sample_rows))

    sections = {
        "Articles by journal": df.group_by("journal")
        .len()
        .sort("len", descending=True),
        "Articles by year": df.group_by("year").len().sort("year"),
        "Articles by source": df.group_by("source").len().sort("len", descending=True),
    }
    for label, table in sections.items():
        typer.echo(f"\n{label}")
        typer.echo(table)

    has_abstract = df.filter(pl.col("abstract").is_not_null()).height
    abstract_summary = pl.DataFrame(
        {
            "status": ["With abstract", "Without abstract"],
            "count": [has_abstract, len(df) - has_abstract],
        }
    ).with_columns(pl.col("count").truediv(len(df)).mul(100).alias("percent"))
    typer.echo("\nAbstract coverage")
    typer.echo(abstract_summary)


def main() -> None:
    """Entry point for console_scripts."""

    app()


if __name__ == "__main__":  # pragma: no cover - Typer handles execution
    main()
