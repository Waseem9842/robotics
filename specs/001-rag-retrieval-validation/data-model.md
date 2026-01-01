# Data Model: RAG Retrieval Validation

## Entities

### Query
- **Description**: A text input from a user that requires semantic matching against stored embeddings
- **Fields**:
  - text: string (the query text)
  - id: string (unique identifier for the query)
  - timestamp: datetime (when the query was created)

### RetrievedChunk
- **Description**: A document segment returned by the retrieval system that matches the query
- **Fields**:
  - id: string (unique identifier for the chunk)
  - text: string (the content of the retrieved chunk)
  - score: float (similarity score between query and chunk)
  - metadata: dict (additional information about the chunk)
  - source_url: string (URL of the original document)
  - collection_name: string (name of the Qdrant collection)

### ValidationResult
- **Description**: The result of validating a retrieval operation
- **Fields**:
  - query_id: string (reference to the original query)
  - retrieved_chunks: list[RetrievedChunk] (list of chunks returned)
  - validation_passed: boolean (whether validation criteria were met)
  - accuracy_score: float (overall accuracy metric)
  - ranking_correctness: float (measure of ranking quality)
  - data_integrity_check: boolean (whether content matches original)

### ValidationTest
- **Description**: A pre-defined test case with expected retrieval outcomes for verification
- **Fields**:
  - id: string (unique identifier for the test)
  - query: Query (the test query)
  - expected_chunks: list[RetrievedChunk] (expected results)
  - threshold: float (minimum similarity score required)
  - top_k: int (number of results to retrieve)

## Relationships
- A Query can have multiple RetrievedChunk results
- A ValidationResult references one Query and multiple RetrievedChunk objects
- A ValidationTest contains one Query and expected RetrievedChunk objects

## Validation Rules
- Query.text must not be empty
- RetrievedChunk.score must be between 0 and 1
- RetrievedChunk.metadata must contain required fields (source_url, collection_name)
- ValidationResult.accuracy_score must be between 0 and 1
- ValidationTest.top_k must be greater than 0