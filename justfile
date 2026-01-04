# Run formatting and type checking
ok:
    ruff format
    ruff check --fix
    ty check

# Run tests
test:
    UV_CACHE_DIR=.uv-cache uv run pytest

# Install as global tool (makes 'ep' and 'econprior' commands available)
install:
    uv tool install --reinstall .

# Download articles
download *ARGS:
    UV_CACHE_DIR=.uv-cache uv run econprior download {{ARGS}}

# Fill missing abstracts from other sources
fill *ARGS:
    UV_CACHE_DIR=.uv-cache uv run econprior fill {{ARGS}}

# Download and fill in one step
download-and-fill *ARGS:
    UV_CACHE_DIR=.uv-cache uv run econprior download {{ARGS}}
    UV_CACHE_DIR=.uv-cache uv run econprior fill {{ARGS}}

# Show database statistics
stats *ARGS:
    UV_CACHE_DIR=.uv-cache uv run econprior stats {{ARGS}}

# Direct CLI passthrough
tool *ARGS:
    UV_CACHE_DIR=.uv-cache uv run econprior {{ARGS}}

stats-sync:
    UV_CACHE_DIR=.uv-cache uv run jupytext --sync notebooks/show_stats.py
    UV_CACHE_DIR=.uv-cache uv run jupyter nbconvert --to notebook --execute --inplace notebooks/show_stats.ipynb

# Copy CLAUDE.md to AGENTS.md
agents:
    cp CLAUDE.md AGENTS.md
