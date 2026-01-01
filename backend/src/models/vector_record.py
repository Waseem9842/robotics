"""Data model for VectorRecord entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class VectorRecord:
    """Represents a complete entry stored in the vector database."""

    id: str
    payload: Dict[str, Any]
    vector: List[float]
    collection_name: str
    created_at: datetime

    def __post_init__(self):
        """Validate the VectorRecord instance after initialization."""
        if not self.id:
            raise ValueError("ID cannot be empty")
        if not self.payload:
            raise ValueError("Payload cannot be empty")
        if not self.vector:
            raise ValueError("Vector cannot be empty")
        if not self.collection_name:
            raise ValueError("Collection name cannot be empty")
        if not isinstance(self.vector, list) or not all(isinstance(v, (int, float)) for v in self.vector):
            raise ValueError("Vector must be a list of numbers")

    @classmethod
    def create(
        cls,
        id: str,
        payload: Dict[str, Any],
        vector: List[float],
        collection_name: str
    ) -> 'VectorRecord':
        """
        Create a VectorRecord instance with validation.

        Args:
            id: Unique identifier for the record
            payload: Contains content, metadata, and references
            vector: The embedding vector
            collection_name: Name of the Qdrant collection

        Returns:
            VectorRecord instance
        """
        return cls(
            id=id,
            payload=payload,
            vector=vector,
            collection_name=collection_name,
            created_at=datetime.now()
        )