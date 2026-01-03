# Plan: Fill Abstracts

## Goal

For articles with null abstracts, try to find the abstract from other sources.

## Tasks

1. Convert show_stats.py to a Jupyter-friendly script paired with a notebook
2. Create a function to fill missing abstracts by checking other sources
3. For each article with null abstract:
   - If from Crossref: try OpenAlex
   - If from OpenAlex: try Crossref
4. Update the database with found abstracts

## Implementation

1. **notebooks/show_stats.py** (paired with `notebooks/show_stats.ipynb`) - Stats notebook conversion
2. **src/econprior/get_data/fill_abstracts.py** - Logic to fill missing abstracts
3. **src/econprior/pipeline/fill_abstracts.py** - CLI to run the fill process
