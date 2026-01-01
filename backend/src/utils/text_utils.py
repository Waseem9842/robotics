"""Utility functions for text processing."""

import re
from typing import List, Tuple


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        # If this isn't the last chunk, try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings near the end of the chunk
            sentence_end = max(chunk.rfind('.'), chunk.rfind('!'), chunk.rfind('?'))
            if sentence_end > chunk_size // 2:  # Only break if it's not too close to the start
                chunk = chunk[:sentence_end + 1]
                end = start + len(chunk)

        chunks.append(chunk)
        start = end - overlap if end - overlap > start else end

    # Remove empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]
    return chunks


def extract_title_from_html(html_content: str) -> str:
    """
    Extract title from HTML content.

    Args:
        html_content: HTML content to extract title from

    Returns:
        Extracted title or empty string if not found
    """
    import re
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        title = title_match.group(1)
        # Remove HTML tags if any remain
        title = re.sub(r'<[^>]+>', '', title)
        return title.strip()
    return ""


def extract_headings_from_html(html_content: str) -> List[str]:
    """
    Extract headings from HTML content.

    Args:
        html_content: HTML content to extract headings from

    Returns:
        List of extracted headings
    """
    import re
    # Find all heading tags (h1-h6)
    headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html_content, re.IGNORECASE)
    # Remove HTML tags from headings and clean them
    cleaned_headings = []
    for heading in headings:
        clean_heading = re.sub(r'<[^>]+>', '', heading)
        clean_heading = clean_text(clean_heading)
        if clean_heading:
            cleaned_headings.append(clean_heading)
    return cleaned_headings