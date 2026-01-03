# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Econpriors is a tool for generating priors for parameters of econometric models, such as elasticities.

## Commands

- `just ok` - Run formatting (ruff) and type checking (ty). Run before committing.
- Use `uv` to run scripts (e.g., `uv run script.py`).

## Workflow

- Create a plan for each feature branch in `docs/plans/`. The plan filename should match the branch name (e.g., branch `get-data` → `docs/plans/get-data.md`).
- When squash merging, format commit message like GitHub:
  ```
  Branch description (#PR_NUMBER or branch name)

  * First commit message
  * Second commit message
  * ...
  ```

## Code Style

- Always use absolute imports.
