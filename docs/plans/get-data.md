# Plan: Get Data

## Goal

Collect article metadata (abstracts, authors, titles, etc.) from the top 5 economics journals and store in SQLite.

## Top 5 Economics Journals

1. American Economic Review (AER) - ISSN: 0002-8282
2. Econometrica - ISSN: 0012-9682
3. Quarterly Journal of Economics (QJE) - ISSN: 0033-5533
4. Journal of Political Economy (JPE) - ISSN: 0022-3808
5. Review of Economic Studies (ReStud) - ISSN: 0034-6527

## Data Sources

- **Crossref API**: Free, no auth required, good coverage of DOIs and metadata
- **OpenAlex API**: Free, no auth required, good abstracts and author info
- **Unpaywall** (optional): For open access links

## Database Schema

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    doi TEXT UNIQUE,
    title TEXT,
    abstract TEXT,
    journal TEXT,
    year INTEGER,
    authors TEXT,  -- JSON array
    source TEXT,   -- 'crossref' or 'openalex'
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_year ON articles(journal, year);
CREATE INDEX idx_doi ON articles(doi);
```

## Core Function Design - roughly

```python
def fetch_journal_year(journal: str, year: int, source: str, conn: sqlite3.Connection) -> int:
    """
    Fetch all articles for a journal/year from specified source.

    - Checks SQLite first for existing entries (by DOI)
    - Only fetches missing articles
    - Returns count of new articles added
    """
```

## Implementation Steps

1. **Database module** (`src/get_data/db.py`)
   - SQLite connection helper
   - Schema creation
   - Insert/check functions

2. **API clients** (`src/get_data/apis/`)
   - `crossref.py`: Fetch by ISSN + year, paginate results
   - `openalex.py`: Fetch by journal + year, paginate results

3. **Main fetcher** (`src/get_data/fetch.py`)
   - `fetch_journal_year(journal, year, source)` function
   - Check existing DOIs before fetching
   - Rate limiting / politeness delays

4. **Script** (`scripts/download_artifcles.py`) (with arguments for year interval )
   - Run fetches for all journals/years
   - Progress reporting

## API Details

### Crossref
- Endpoint: `https://api.crossref.org/journals/{issn}/works`
- Filter by year: `?filter=from-pub-date:{year},until-pub-date:{year}`
- Paginate with `cursor` parameter
- Rate limit: Be polite, use `mailto` parameter

### OpenAlex
- Endpoint: `https://api.openalex.org/works`
- Filter: `?filter=primary_location.source.issn:{issn},publication_year:{year}`
- Paginate with `cursor` parameter
- Good abstract coverage via `abstract_inverted_index`

## Order of Implementation

1. Database module with schema
2. Crossref client (simpler API)
3. Main fetch function with dedup logic
4. OpenAlex client
5. CLI for batch fetching
6. Tests
