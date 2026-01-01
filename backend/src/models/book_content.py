"""Data model for BookContent entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class BookContent:
    """Represents the text content extracted from deployed book URLs."""

    id: str
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime

    def __post_init__(self):
        """Validate the BookContent instance after initialization."""
        if not self.id:
            raise ValueError("ID cannot be empty")
        if not self.url:
            raise ValueError("URL cannot be empty")
        if not self.content:
            raise ValueError("Content cannot be empty")

    @classmethod
    def create(
        cls,
        id: str,
        url: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'BookContent':
        """
        Create a BookContent instance with validation.

        Args:
            id: Unique identifier for the content chunk
            url: Source URL of the book page
            title: Title of the book page
            content: Extracted text content
            metadata: Additional metadata (section, hierarchy, etc.)

        Returns:
            BookContent instance
        """
        if metadata is None:
            metadata = {}

        return cls(
            id=id,
            url=url,
            title=title,
            content=content,
            metadata=metadata,
            created_at=datetime.now()
        )