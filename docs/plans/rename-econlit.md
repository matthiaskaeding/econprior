# Plan: Rename Econpriors to Econlit

## Goal

Update the repository so everything consistently uses the new `econlit` name (package metadata, docs, tooling) and confirm the renamed project still builds and tests cleanly.

## Tasks

1. Audit the repo for stale `econpriors` references (package imports, docs, packaging metadata) and update them to `econlit`.
2. Ensure `pyproject.toml` and `uv.lock` describe the `econlit` package and its runtime dependencies accurately so packaging continues to work after the rename.
3. Run `just ok` and `just test` to confirm formatting, type checking, and tests pass under the new name.

## Implementation

1. `pyproject.toml` / `uv.lock` – Update the package metadata and dependencies to match the renamed module layout.
2. Repository-wide text search – Verify no lingering `econpriors` identifiers remain in source, docs, or configs.
3. `justfile` workflows – Use the standard `just` commands to validate formatting, type checking, and test execution once the rename is complete.
