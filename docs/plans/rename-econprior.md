# Plan: Rename Econlit Back to Econprior

## Goal

Revert the recent rename so the package, docs, and tooling consistently use the original `econprior` name, while ensuring packaging and tests continue to work.

## Tasks

1. Update project metadata (`pyproject.toml`, `uv.lock`, docs) from `econlit` back to `econprior`.
2. Rename the `src/econlit` package directory and any imports/usages back to `src/econprior`.
3. Verify no lingering `econlit` references remain via repository-wide search.
4. Run `just ok` and `just test` to ensure formatting, type checking, and tests still pass post-rename.

## Implementation

1. Use `git mv` to rename the package path and adjust absolute imports accordingly.
2. Edit metadata/config files to reference `econprior`, then regenerate the lockfile if needed.
3. Execute `just ok` / `just test` to validate the changed codebase.
