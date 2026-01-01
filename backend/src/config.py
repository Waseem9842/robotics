"""Configuration module to handle environment variables."""

import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to manage environment variables."""

    # Cohere API Configuration
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    # Qdrant Configuration
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "book_embeddings")

    # Application Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

    @classmethod
    def validate(cls):
        """Validate that required configuration values are present."""
        required_vars = ["COHERE_API_KEY", "QDRANT_API_KEY", "QDRANT_HOST"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")