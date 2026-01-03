# Econprior

Econprior collects top-journal articles, stores them in SQLite, and offers utilities to inspect statistics and fill in missing abstracts.

Upcoming work: feed the cleaned corpus into an RAG pipeline so we can answer economic questions across the literature.

## CLI

The Typer-based CLI wraps all workflows. Run it via `uv` (which respects the local virtualenv):

```sh
uv run econprior --help             # list commands
uv run econprior download -h        # show command-specific options
uv run econprior download --start-year 2015 --end-year 2020 --journals aer,qje
uv run econprior fill
uv run econprior stats
```

`just download`, `just fill`, and `just stats` are thin wrappers around the same CLI if you prefer the `just` workflow.
