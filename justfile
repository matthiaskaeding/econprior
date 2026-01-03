# Run formatting and type checking
ok:
    ruff format
    ruff check --fix
    ty check

# Copy CLAUDE.md to AGENTS.md
agents:
    cp CLAUDE.md AGENTS.md
