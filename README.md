# Econprior

Econprior collects top-journal articles, stores them in SQLite, and offers utilities to inspect statistics and fill in missing abstracts.

Upcoming work: feed the cleaned corpus into an RAG pipeline so we can answer economic questions across the literature.

## Installation

Install econprior globally to make the `ep` and `econprior` commands available from anywhere:

```sh
just install
```

This runs `uv tool install --reinstall .` and makes both commands available in your PATH.

## CLI Usage

After installation, use the short `ep` command or full `econprior` command:

```sh
ep --help                           # list all commands
ep download -h                      # show command-specific options
ep download --start-year 2015 --end-year 2020 --journals aer,qje
ep fill                             # fill missing abstracts
ep stats                            # show database statistics

# Or use the full name:
econprior download --start-year 2020
```

## Development Workflow

**Option 1: Use installed commands (recommended)**
```sh
# Make code changes...
just ok                             # format and type check
just install                        # reinstall with latest changes
ep download                         # use the updated command
```

**Option 2: Run without installing**
```sh
# Make code changes...
uv run ep download                  # run from local venv
uv run econprior stats              # test without installing
```

## Just Commands

Convenience wrappers for common tasks:

```sh
just install         # Install as global tool (makes 'ep' available)
just ok              # Run formatting and type checking
just test            # Run tests
just download        # Download articles (wrapper around CLI)
just fill            # Fill missing abstracts (wrapper around CLI)
just stats           # Show database statistics (wrapper around CLI)
```
