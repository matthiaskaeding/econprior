# Run formatting and type checking
ok:
    ruff format
    ruff check --fix
    ty check

# Run tests
test:
    UV_CACHE_DIR=.uv-cache uv run --group dev pytest

# Download articles
download *ARGS:
    UV_CACHE_DIR=.uv-cache uv run scripts/download_articles.py {{ARGS}}

# Fill missing abstracts from other sources
fill *ARGS:
    UV_CACHE_DIR=.uv-cache uv run scripts/fill_abstracts.py {{ARGS}}

# Download and fill in one step
download-and-fill *ARGS:
    just download {{ARGS}}
    just fill {{ARGS}}

# Show database statistics
stats:
    UV_CACHE_DIR=.uv-cache uv run python scripts/show_stats.py

stats-sync:
    UV_CACHE_DIR=.uv-cache uv run jupytext --sync scripts/show_stats.py
    UV_CACHE_DIR=.uv-cache uv run python -m jupyter nbconvert --to notebook --execute --inplace notebooks/show_stats.ipynb

# Copy CLAUDE.md to AGENTS.md
agents:
    cp CLAUDE.md AGENTS.md
