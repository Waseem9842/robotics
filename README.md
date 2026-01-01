# RAG Agent with OpenAI Agents SDK

This project implements a Retrieval-Augmented Generation (RAG) agent that integrates with Qdrant for document retrieval and uses OpenAI's API for response generation. It also includes validation for RAG retrieval accuracy.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=your_collection_name
MODEL_NAME=gpt-4-turbo
TEMPERATURE=0.1
TOP_K=5
GROUNDING_THRESHOLD=0.5
COHERE_API_KEY=your_cohere_api_key
```

## Usage

### RAG Agent
Run the main agent:
```bash
python agent.py
```

The agent will prompt you for questions and respond based on the retrieved context from Qdrant.

### RAG Retrieval Validation
Run the retrieval validation:
```bash
python backend/retrieve.py --query "your test query" --top-k 5 --threshold 0.7
```

#### RAG Agent Options
The agent behavior can be configured via environment variables:
- `MODEL_NAME`: OpenAI model to use (default: gpt-4-turbo)
- `TEMPERATURE`: Response creativity (default: 0.1 for factual responses)
- `TOP_K`: Number of context items to retrieve (default: 5)
- `GROUNDING_THRESHOLD`: Minimum relevance score for context inclusion (default: 0.5)

#### Retrieval Validation Options
- `--query`: The test query to validate (required)
- `--collection`: Qdrant collection name (optional, will auto-detect if not specified)
- `--top-k`: Number of results to retrieve (default: 5)
- `--threshold`: Minimum similarity score (default: 0.7)

## Example

### RAG Agent
```bash
python agent.py
```
Then ask questions like "What are the main concepts in robotics?"

### Retrieval Validation
```bash
python backend/retrieve.py --query "What is the capital of France?" --top-k 3 --threshold 0.6
```

## Features

- Natural language question processing (RAG Agent)
- Integration with Qdrant vector database for context retrieval
- Responses grounded only in retrieved content (no hallucination)
- Deterministic and testable behavior
- Comprehensive error handling for edge cases
- Retrieval validation with accuracy assessment
- Data integrity checks

## Architecture

- `agent.py`: Main agent implementation with Qdrant integration
- `src/qdrant_client.py`: Qdrant client utility for context retrieval
- `src/config.py`: Configuration management
- `src/grounding_validator.py`: Response grounding validation
- `backend/retrieve.py`: Retrieval validation functionality
- `tests/`: Unit and integration tests

## Testing

Run all tests:
```bash
pytest
```

Run specific test directories:
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/test_agent.py
pytest tests/test_retrieval.py
```