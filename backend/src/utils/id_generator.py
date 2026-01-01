"""Utility functions for ID generation."""

import uuid
import hashlib
from datetime import datetime
from typing import Optional


def generate_content_id(url: str, content: str = "") -> str:
    """
    Generate a unique content ID based on URL and content.

    Args:
        url: The URL of the content
        content: The content itself (optional, for more uniqueness)

    Returns:
        Unique identifier string
    """
    if content:
        # Create hash from URL + content
        combined = f"{url}:{content[:100]}"  # Use first 100 chars to avoid long processing
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    else:
        # Create hash from URL only
        return hashlib.sha256(url.encode()).hexdigest()[:16]


def generate_embedding_id(content_id: str, model_name: str) -> str:
    """
    Generate a unique embedding ID based on content ID and model name.

    Args:
        content_id: The ID of the associated content
        model_name: The name of the embedding model used

    Returns:
        Unique identifier string
    """
    combined = f"{content_id}:{model_name}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def generate_vector_record_id(content_id: str, vector: list) -> str:
    """
    Generate a unique vector record ID based on content ID and vector.

    Args:
        content_id: The ID of the associated content
        vector: The embedding vector

    Returns:
        Unique identifier string
    """
    # Use first few elements of vector for uniqueness without full processing
    vector_str = ":".join([str(x) for x in vector[:5]]) if vector else ""
    combined = f"{content_id}:{vector_str}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def generate_uuid() -> str:
    """
    Generate a standard UUID.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def generate_timestamp_id() -> str:
    """
    Generate an ID based on current timestamp.

    Returns:
        Timestamp-based identifier string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    unique_part = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_part}"