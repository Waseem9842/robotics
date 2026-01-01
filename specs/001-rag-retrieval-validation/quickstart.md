# Quickstart: RAG Retrieval Validation

## Setup

1. Install dependencies:
```bash
pip install qdrant-client cohere python-dotenv pytest
```

2. Create a `.env` file with your API keys:
```env
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
COHERE_API_KEY=your_cohere_api_key
```

3. Ensure you have existing vector collections in Qdrant with Cohere embeddings.

## Usage

Run the retrieval validation:

```bash
python backend/retrieve.py --query "your test query" --top-k 5 --threshold 0.7
```

## Configuration

- `--query`: The test query to validate (required)
- `--top-k`: Number of results to retrieve (default: 5)
- `--threshold`: Minimum similarity score (default: 0.7)
- `--collection`: Qdrant collection name (optional, will auto-detect if not specified)

## Validation Output

The script will output:
- Retrieved chunks with similarity scores
- Validation results (pass/fail)
- Accuracy metrics
- Ranking correctness assessment
- Data integrity check results