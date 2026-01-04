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

# Sync notebooks with their paired .py files
nbsync:
    uv run jupytext --sync notebooks/*.py

# Copy CLAUDE.md to AGENTS.md
agents:
    cp CLAUDE.md AGENTS.md
