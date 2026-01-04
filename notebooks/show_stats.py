# ---
# jupyter:
#   jupytext:
#     formats: notebooks//py:percent,notebooks//ipynb
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Article statistics
#
# Inspect downloaded article metadata stored in `data/articles.db`.

# %%
from pathlib import Path

import polars as pl


# %%
if "__file__" in globals():
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
else:
    PROJECT_ROOT = Path.cwd().parent

DB_PATH = PROJECT_ROOT / "data" / "articles.db"
DB_URI = f"sqlite:///{DB_PATH.expanduser().resolve().as_posix()}"
print(f"Reading articles from {DB_URI}")


# %%
QUERY = "SELECT * FROM articles"
df = pl.read_database_uri(QUERY, DB_URI)
print(f"Loaded {len(df)} articles")


# %% [markdown]
# ## Overview

# %%
summary = pl.DataFrame(
    {
        "metric": ["Total articles", "DataFrame shape", "Columns"],
        "value": [
            str(len(df)),
            f"{df.shape[0]} rows x {df.shape[1]} cols",
            ", ".join(df.columns),
        ],
    }
)
print("\n" + "=" * 60)
print("ARTICLES DATABASE OVERVIEW")
print("=" * 60)
print(summary)


# %% [markdown]
# ## Sample data

# %%
print("\n" + "-" * 60)
print("SAMPLE DATA (first 5 rows)")
print("-" * 60)
sample_rows = df.head()
print(sample_rows)


# %% [markdown]
# ## Articles by journal

# %%
print("\n" + "-" * 60)
print("ARTICLES BY JOURNAL")
print("-" * 60)
by_journal = df.group_by("journal").len().sort("len", descending=True)
print(by_journal)


# %% [markdown]
# ## Articles by year

# %%
print("\n" + "-" * 60)
print("ARTICLES BY YEAR")
print("-" * 60)
by_year = df.group_by("year").len().sort("year")
print(by_year)


# %% [markdown]
# ## Articles by source

# %%
print("\n" + "-" * 60)
print("ARTICLES BY SOURCE")
print("-" * 60)
by_source = df.group_by("source").len().sort("len", descending=True)
print(by_source)


# %% [markdown]
# ## Abstract coverage

# %%
has_abstract = df.filter(pl.col("abstract").is_not_null()).height
abstract_summary = pl.DataFrame(
    {
        "status": ["With abstract", "Without abstract"],
        "count": [has_abstract, len(df) - has_abstract],
    }
).with_columns(pl.col("count").truediv(len(df)).mul(100).alias("percent"))
print("\n" + "-" * 60)
print("ABSTRACT COVERAGE")
print("-" * 60)
print(abstract_summary)


# %% [markdown]
# ### Abstract coverage by journal

# %%
print("\n" + "-" * 60)
print("ABSTRACT COVERAGE BY JOURNAL")
print("-" * 60)
abstract_by_journal = df.group_by("journal").agg(
    [
        pl.len().alias("total"),
        pl.col("abstract").is_not_null().sum().alias("with_abstract"),
    ]
)
abstract_by_journal = abstract_by_journal.with_columns(
    (pl.col("total") - pl.col("with_abstract")).alias("without_abstract")
).with_columns(
    (pl.col("without_abstract") / pl.col("total") * 100).alias("percent_without")
)
abstract_by_journal = abstract_by_journal.select(
    [
        pl.col("journal"),
        pl.col("without_abstract"),
        pl.col("percent_without"),
    ]
).sort("percent_without", descending=True)
print(abstract_by_journal)


# %% [markdown]
# ### Abstract coverage by source

# %%
print("\n" + "-" * 60)
print("ABSTRACT COVERAGE BY SOURCE")
print("-" * 60)
abstract_by_source = df.group_by("source").agg(
    [
        pl.len().alias("total"),
        pl.col("abstract").is_not_null().sum().alias("with_abstract"),
    ]
)
abstract_by_source = abstract_by_source.with_columns(
    (pl.col("total") - pl.col("with_abstract")).alias("without_abstract")
).with_columns(
    (pl.col("without_abstract") / pl.col("total") * 100).alias("percent_without")
)
abstract_by_source = abstract_by_source.select(
    [
        pl.col("source"),
        pl.col("without_abstract"),
        pl.col("percent_without"),
    ]
).sort("percent_without", descending=True)
print(abstract_by_source)
