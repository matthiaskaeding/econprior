import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    doi TEXT UNIQUE,
    title TEXT,
    abstract TEXT,
    journal TEXT,
    year INTEGER,
    authors TEXT,
    source TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_journal_year ON articles(journal, year);
CREATE INDEX IF NOT EXISTS idx_doi ON articles(doi);
"""


DEFAULT_DB_PATH = Path("data") / "articles.db"


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def doi_exists(conn: sqlite3.Connection, doi: str) -> bool:
    cursor = conn.execute("SELECT 1 FROM articles WHERE doi = ?", (doi,))
    return cursor.fetchone() is not None


def get_existing_dois(conn: sqlite3.Connection, journal: str, year: int) -> set[str]:
    cursor = conn.execute(
        "SELECT doi FROM articles WHERE journal = ? AND year = ?", (journal, year)
    )
    return {row["doi"] for row in cursor.fetchall()}


def insert_article(
    conn: sqlite3.Connection,
    doi: str,
    title: str,
    abstract: str | None,
    journal: str,
    year: int,
    authors: list[str],
    source: str,
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO articles (doi, title, abstract, journal, year, authors, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (doi, title, abstract, journal, year, json.dumps(authors), source),
    )
