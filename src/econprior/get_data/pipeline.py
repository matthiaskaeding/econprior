"""Data pipelines for downloading metadata and filling abstracts."""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Iterable, Literal, Sequence

import polars as pl
from tqdm import tqdm

from econprior.get_data import db
from econprior.get_data.fetch import fetch_journal_year
from econprior.get_data.fill_abstracts import (
    fill_missing_abstracts,
    get_articles_missing_abstract,
)
from econprior.get_data.journals import JOURNALS

SourceOption = Literal["crossref", "openalex"]


def _resolve_db(path: Path) -> Path:
    return path.expanduser().resolve()


def _normalize_journals(journals: Sequence[str] | None) -> list[str]:
    if journals:
        selected = [j.strip() for j in journals if j.strip()]
    else:
        selected = list(JOURNALS.keys())

    missing = sorted(set(selected) - set(JOURNALS.keys()))
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"Unknown journals: {missing_list}")

    return selected


def download_articles(
    *,
    start_year: int,
    end_year: int,
    source: SourceOption,
    journals: Sequence[str] | None,
    db_path: Path,
    show_progress: bool = True,
) -> int:
    """Download article metadata into the local SQLite database."""

    if start_year > end_year:
        raise ValueError("start_year must be <= end_year")

    selected_journals = _normalize_journals(journals)
    resolved_db = _resolve_db(db_path)
    conn = db.get_connection(resolved_db)
    db.init_db(conn)

    try:
        tasks = list(
            itertools.product(selected_journals, range(start_year, end_year + 1))
        )
        progress = (
            tqdm(tasks, desc=f"Fetching from {source}") if show_progress else None
        )
        iterator: Iterable[tuple[str, int]]
        iterator = progress or tasks

        total = 0
        for journal, year in iterator:
            count = fetch_journal_year(journal, year, source, conn)
            total += count
            if progress:
                progress.set_postfix({"journal": journal, "year": year})
        if progress:
            progress.close()
    finally:
        conn.close()

    return total


def fill_missing_abstracts_pipeline(
    *,
    db_path: Path,
    show_progress: bool = True,
) -> tuple[int, int]:
    """Fill missing abstracts using the opposite source."""

    resolved_db = _resolve_db(db_path)
    conn = db.get_connection(resolved_db)

    try:
        missing = get_articles_missing_abstract(conn)
        if not missing:
            return 0, 0

        progress = (
            tqdm(total=len(missing), desc="Filling abstracts")
            if show_progress
            else None
        )

        def on_progress(article: dict, target_source: str, success: bool) -> None:
            if not progress:
                return
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
        if progress:
            progress.close()

        return len(missing), filled
    finally:
        conn.close()


def load_articles_dataframe(db_path: Path) -> pl.DataFrame:
    """Load the articles table into a Polars DataFrame."""

    resolved_db = _resolve_db(db_path)
    conn_uri = f"sqlite:///{resolved_db.as_posix()}"
    return pl.read_database_uri("SELECT * FROM articles", conn_uri)
