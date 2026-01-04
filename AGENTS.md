# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Econprior is a tool for generating priors for parameters of econometric models, such as elasticities.

## Commands

- `just ok` - Run formatting (ruff) and type checking (ty). Run before committing.
- `just test` - Run tests.
- `just install` - Install as global tool (makes `ep` and `econprior` commands available).
- `just download` - Download articles from top 5 econ journals.
- `just stats` - Show database statistics.
- Use the packaged CLI for workflows: `uv run econprior --help`, `uv run econprior download -h`, `uv run econprior fill`, etc.
- Run arbitrary scripts with `uv` (e.g., `uv run script.py`) when needed.
- **IMPORTANT**: Use `uv run -m module` instead of `uv run python -m module`. Examples:
  - ✅ `uv run -m econprior.cli`
  - ❌ `uv run python -m econprior.cli`

## Workflow

- Create a plan for each feature branch in `docs/plans/`. The plan filename should match the branch name (e.g., branch `get-data` → `docs/plans/get-data.md`).
- When squash merging, format commit message like GitHub:
  ```
  Branch description (#PR_NUMBER or branch name)

  * First commit message
  * Second commit message
  * ...
  ```

## Sample Data

Sample data with synthetic abstracts is available in `data/sample.csv` for quick testing or Claude web usage.

## Code Style

- Always use absolute imports.
- When using `uv run` with Python modules, use `uv run -m` directly, NOT `uv run python -m`.
