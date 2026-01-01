"""Data model for EmbeddingVector entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class EmbeddingVector:
    """Represents the numerical vector representation of text content."""

    id: str
    vector: List[float]
    content_id: str
    model_name: str
    created_at: datetime

    def __post_init__(self):
        """Validate the EmbeddingVector instance after initialization."""
        if not self.id:
            raise ValueError("ID cannot be empty")
        if not self.vector:
            raise ValueError("Vector cannot be empty")
        if not self.content_id:
            raise ValueError("Content ID cannot be empty")
        if not self.model_name:
            raise ValueError("Model name cannot be empty")
        if not isinstance(self.vector, list) or not all(isinstance(v, (int, float)) for v in self.vector):
            raise ValueError("Vector must be a list of numbers")

    @classmethod
    def create(
        cls,
        id: str,
        vector: List[float],
        content_id: str,
        model_name: str
    ) -> 'EmbeddingVector':
        """
        Create an EmbeddingVector instance with validation.

        Args:
            id: Unique identifier for the vector (matches BookContent.id)
            vector: Numerical vector representation from embedding model
            content_id: Reference to associated BookContent
            model_name: Name of the embedding model used

        Returns:
            EmbeddingVector instance
        """
        return cls(
            id=id,
            vector=vector,
            content_id=content_id,
            model_name=model_name,
            created_at=datetime.now()
        )