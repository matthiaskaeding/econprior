# Run formatting and type checking
ok:
    ruff format
    ruff check --fix
    ty check

# Run tests
test:
    uv run pytest

# Download articles
download *ARGS:
    uv run scripts/download_articles.py {{ARGS}}

# Show database statistics
stats *ARGS:
    uv run scripts/show_stats.py {{ARGS}}

# Copy CLAUDE.md to AGENTS.md
agents:
    cp CLAUDE.md AGENTS.md
