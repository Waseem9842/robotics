# Data Model: Embeddings Vector Storage Pipeline

## Entities

### BookContent
**Description**: Represents the text content extracted from deployed book URLs

**Fields**:
- `id` (string): Unique identifier for the content chunk
- `url` (string): Source URL of the book page
- `title` (string): Title of the book page
- `content` (string): Extracted text content
- `metadata` (dict): Additional metadata (section, hierarchy, etc.)
- `created_at` (datetime): Timestamp of extraction

**Validation**:
- URL must be a valid, accessible web address
- Content must not be empty
- Metadata should include source tracking information

### EmbeddingVector
**Description**: Represents the numerical vector representation of text content

**Fields**:
- `id` (string): Unique identifier for the vector (matches BookContent.id)
- `vector` (list[float]): Numerical vector representation from embedding model
- `content_id` (string): Reference to associated BookContent
- `model_name` (string): Name of the embedding model used
- `created_at` (datetime): Timestamp of embedding generation

**Validation**:
- Vector must be a valid numerical array
- Content_id must reference an existing BookContent
- Model name must be a valid Cohere model

### VectorRecord
**Description**: Represents a complete entry stored in the vector database

**Fields**:
- `id` (string): Unique identifier for the record
- `payload` (dict): Contains content, metadata, and references
- `vector` (list[float]): The embedding vector
- `collection_name` (string): Name of the Qdrant collection
- `created_at` (datetime): Timestamp of storage

**Validation**:
- Must contain valid vector data
- Payload must include required metadata
- Collection must exist in Qdrant

## Relationships

1. **BookContent → EmbeddingVector**: One-to-one relationship (each content chunk has one vector representation)
2. **EmbeddingVector → VectorRecord**: One-to-one relationship (each embedding becomes one stored record)
3. **VectorRecord**: Self-contained entity stored in Qdrant with all necessary metadata

## State Transitions

1. **Raw URL** → **BookContent**: Content extraction and cleaning
2. **BookContent** → **EmbeddingVector**: Embedding generation
3. **EmbeddingVector** → **VectorRecord**: Storage in vector database
4. **VectorRecord**: Available for similarity search and retrieval