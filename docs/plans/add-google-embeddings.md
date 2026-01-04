# Plan: Add Google Embeddings

**Branch:** `claude/add-google-embeddings-RND6I`

## Goal

Generate embeddings for article abstracts and titles using Google's embedding model via LangChain. This will enable semantic search and similarity analysis of economic research papers.

## Approach

Start simple with a basic implementation that:
1. Adds LangChain and Google GenAI dependencies
2. Creates a module to generate embeddings from text (title + abstract)
3. Adds a CLI command to generate and store embeddings
4. Stores embeddings in the SQLite database

## Implementation Steps

### 1. Add Dependencies
- Add `langchain` and `langchain-google-genai` to pyproject.toml
- Google API key will be read from environment variable `GOOGLE_API_KEY`

### 2. Create Embeddings Module
- New module: `src/econprior/embeddings/embed.py`
- Function to combine title + abstract into a single text
- Function to generate embeddings using Google's embedding model
- Use `models/embedding-001` (Google's text embedding model)

### 3. Update Database Schema
- Add new table `embeddings` with columns:
  - `id` (INTEGER PRIMARY KEY)
  - `doi` (TEXT, foreign key to articles.doi)
  - `embedding` (BLOB, stores the vector as bytes)
  - `model` (TEXT, stores model name like "google-embedding-001")
  - `created_at` (TIMESTAMP)
- Add index on doi for fast lookups

### 4. Add CLI Command
- New command: `econprior embed`
- Options:
  - `--db`: Path to database (default: data/articles.db)
  - `--batch-size`: Number of articles to process at once (default: 10)
  - `--force`: Re-generate embeddings even if they exist
- Shows progress with tqdm
- Skips articles without abstracts

### 5. Basic Usage Flow
```bash
export GOOGLE_API_KEY="your-api-key"
uv run econprior embed --db data/articles.db
```

## Future Enhancements (Not in this PR)
- Similarity search functionality
- Vector database integration (e.g., ChromaDB, FAISS)
- Caching strategies
- Support for other embedding models
- Batch processing optimizations

## Testing
- Test with sample.csv data first
- Verify embeddings are generated and stored correctly
- Check embedding dimensions match model output (768 for embedding-001)

## Notes
- Keep it simple for initial implementation
- Focus on getting the pipeline working end-to-end
- Can optimize batch processing and storage later
