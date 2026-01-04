# Plan: Typer CLI

## Goal

Provide a first-class Typer CLI that lives inside the `econprior` package so it can be invoked with `uv run` or through an installed console script.

## Tasks

1. Move the Typer app from `scripts/cli.py` into `src/econprior/cli.py` and update imports to match the package name.
2. Wire the CLI into packaging by adding a `project.scripts` entry for `econprior` in `pyproject.toml`.
3. Update automation (`justfile`) and docs/instructions to reference the packaged CLI (e.g., `uv run python -m econprior.cli ...`).
