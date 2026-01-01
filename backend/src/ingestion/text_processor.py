"""Module for cleaning and chunking text."""

from typing import List, Dict, Any
from src.utils.text_utils import clean_text, chunk_text
from src.utils.logger import app_logger
from src.exceptions import ValidationError
from src.config import Config


class TextProcessor:
    """Class to handle text cleaning and chunking operations."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the text processor.

        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

    def clean(self, text: str) -> str:
        """
        Clean the input text.

        Args:
            text: Input text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        cleaned_text = clean_text(text)
        app_logger.debug(f"Cleaned text from {len(text)} to {len(cleaned_text)} characters")
        return cleaned_text

    def chunk(self, text: str) -> List[str]:
        """
        Chunk the input text into overlapping pieces.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
        app_logger.debug(f"Chunked text into {len(chunks)} chunks")
        return chunks

    def process(self, text: str) -> List[str]:
        """
        Clean and chunk the input text.

        Args:
            text: Input text to process

        Returns:
            List of processed text chunks
        """
        if not text:
            return []

        # Clean the text first
        cleaned_text = self.clean(text)

        # Then chunk it
        chunks = self.chunk(cleaned_text)

        app_logger.info(f"Processed text into {len(chunks)} chunks")
        return chunks

    def validate_chunk(self, chunk: str) -> bool:
        """
        Validate that a chunk meets requirements.

        Args:
            chunk: Text chunk to validate

        Returns:
            True if valid, False otherwise
        """
        if not chunk or not chunk.strip():
            return False

        # Check if chunk is too short (less than 10 characters)
        if len(chunk.strip()) < 10:
            return False

        return True

    def process_with_validation(self, text: str) -> List[str]:
        """
        Clean, chunk, and validate the input text.

        Args:
            text: Input text to process

        Returns:
            List of validated text chunks
        """
        chunks = self.process(text)
        validated_chunks = [chunk for chunk in chunks if self.validate_chunk(chunk)]

        app_logger.info(f"Validated {len(validated_chunks)} out of {len(chunks)} chunks")
        return validated_chunks