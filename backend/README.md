# Embeddings Vector Storage Pipeline

This project implements a URL ingestion and embedding pipeline that extracts content from deployed book URLs, generates vector embeddings using Cohere models, and stores them in Qdrant Cloud vector database.

## Prerequisites

- Python 3.11+
- `uv` package manager installed
- Cohere API key
- Qdrant Cloud cluster access

## Setup

1. **Install dependencies using uv**:
   ```bash
   cd backend
   uv sync
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_HOST=your_qdrant_cluster_url
   ```

## Usage

### Run the full ingestion pipeline

```bash
python main.py
```

This will execute the complete pipeline:
1. Fetch content from configured book URLs
2. Clean and chunk the text
3. Generate embeddings using Cohere
4. Store vectors in Qdrant Cloud

### Run individual components (for development)

```bash
# Just content extraction
python -m src.ingestion.url_fetcher --url "https://your-book-url.com"

# Just embedding generation
python -m src.embeddings.generator --text "your text here"

# Just vector storage
python -m src.storage.vector_store --vector "[0.1, 0.2, 0.3]"
```

## Configuration

The pipeline can be configured via:
- Environment variables in `.env`
- Command line arguments to `main.py`
- Configuration file (to be implemented)

## Testing

Run the full test suite:
```bash
pytest
```

Run specific tests:
```bash
# Test ingestion
pytest tests/test_ingestion.py

# Test embeddings
pytest tests/test_embeddings.py

# Test storage
pytest tests/test_storage.py
```