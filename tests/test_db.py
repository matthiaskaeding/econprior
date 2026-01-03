import sqlite3

from econpriors.get_data import db


def test_init_db_creates_table() -> None:
    conn = sqlite3.connect(":memory:")
    db.init_db(conn)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='articles'"
    )
    assert cursor.fetchone() is not None


def test_insert_and_check_doi() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    db.init_db(conn)

    assert not db.doi_exists(conn, "10.1234/test")

    db.insert_article(
        conn,
        doi="10.1234/test",
        title="Test Article",
        abstract="This is a test.",
        journal="Test Journal",
        year=2024,
        authors=["John Doe", "Jane Doe"],
        source="crossref",
    )
    conn.commit()

    assert db.doi_exists(conn, "10.1234/test")


def test_get_existing_dois() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    db.init_db(conn)

    db.insert_article(
        conn,
        doi="10.1234/a",
        title="Article A",
        abstract=None,
        journal="Test Journal",
        year=2024,
        authors=[],
        source="crossref",
    )
    db.insert_article(
        conn,
        doi="10.1234/b",
        title="Article B",
        abstract=None,
        journal="Test Journal",
        year=2024,
        authors=[],
        source="crossref",
    )
    db.insert_article(
        conn,
        doi="10.1234/c",
        title="Article C",
        abstract=None,
        journal="Other Journal",
        year=2024,
        authors=[],
        source="crossref",
    )
    conn.commit()

    dois = db.get_existing_dois(conn, "Test Journal", 2024)
    assert dois == {"10.1234/a", "10.1234/b"}
