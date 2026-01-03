"""Typer-based CLI for econprior utility scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import polars as pl
import typer

from econprior.get_data.pipeline import (
    SourceOption,
    download_articles,
    fill_missing_abstracts_pipeline,
    load_articles_dataframe,
)


app = typer.Typer(
    help="CLI entry point for econprior scripting utilities.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


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

    selected_journals = (
        [j.strip() for j in journals.split(",") if j.strip()] if journals else None
    )

    try:
        total = download_articles(
            start_year=start_year,
            end_year=end_year,
            source=source,
            journals=selected_journals,
            db_path=db_path,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Total: {total} new articles added")


@app.command()
def fill(
    db_path: Path = typer.Option(
        Path("data/articles.db"), "--db", help="Path to the SQLite database"
    ),
) -> None:
    """Fill missing abstracts using the opposite source."""

    missing, filled = fill_missing_abstracts_pipeline(db_path=db_path)
    typer.echo(f"Found {missing} articles with missing abstracts")

    if not missing:
        return

    typer.echo(f"Filled {filled} abstracts")


@app.command()
def stats(
    db_path: Path = typer.Option(
        Path("data/articles.db"), "--db", help="Path to the SQLite database"
    ),
    sample_rows: int = typer.Option(5, help="Number of sample rows to display"),
) -> None:
    """Print summary statistics about the stored articles."""

    resolved_db = db_path.expanduser().resolve()
    conn_uri = f"sqlite:///{resolved_db.as_posix()}"
    typer.echo(f"Reading articles from {conn_uri}")

    df = load_articles_dataframe(resolved_db)
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
