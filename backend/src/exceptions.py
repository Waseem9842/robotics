"""Custom exceptions for the embeddings pipeline."""


class EmbeddingPipelineError(Exception):
    """Base exception for the embeddings pipeline."""
    pass


class ContentExtractionError(EmbeddingPipelineError):
    """Raised when content extraction fails."""
    pass


class EmbeddingGenerationError(EmbeddingPipelineError):
    """Raised when embedding generation fails."""
    pass


class VectorStorageError(EmbeddingPipelineError):
    """Raised when vector storage operations fail."""
    pass


class ConfigurationError(EmbeddingPipelineError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(EmbeddingPipelineError):
    """Raised when validation fails."""
    pass


class URLValidationError(EmbeddingPipelineError):
    """Raised when URL validation fails."""
    pass


class QdrantConnectionError(EmbeddingPipelineError):
    """Raised when connection to Qdrant fails."""
    pass


class SimilaritySearchError(EmbeddingPipelineError):
    """Raised when similarity search operations fail."""
    pass