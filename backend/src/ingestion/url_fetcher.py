"""Module for fetching and extracting content from URLs."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time

from src.config import Config
from src.exceptions import ContentExtractionError, URLValidationError
from src.utils.logger import app_logger
from src.models.book_content import BookContent
from src.utils.id_generator import generate_content_id


class URLFetcher:
    """Class to handle URL fetching and content extraction."""

    def __init__(self):
        """Initialize the URL fetcher with configuration."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; EmbeddingPipeline/1.0)'
        })

    def fetch_content(self, url: str) -> str:
        """
        Fetch content from a given URL.

        Args:
            url: URL to fetch content from

        Returns:
            HTML content as string

        Raises:
            ContentExtractionError: If fetching fails
            URLValidationError: If URL is invalid
        """
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise URLValidationError(f"Invalid URL format: {url}")

        try:
            app_logger.info(f"Fetching content from URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes

            app_logger.info(f"Successfully fetched content from {url}")
            return response.text

        except requests.exceptions.RequestException as e:
            app_logger.error(f"Error fetching content from {url}: {str(e)}")
            raise ContentExtractionError(f"Failed to fetch content from {url}: {str(e)}")
        except Exception as e:
            app_logger.error(f"Unexpected error fetching content from {url}: {str(e)}")
            raise ContentExtractionError(f"Unexpected error fetching content from {url}: {str(e)}")

    def extract_content_from_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract meaningful content from HTML.

        Args:
            html_content: Raw HTML content
            url: Source URL for metadata

        Returns:
            Dictionary with extracted content and metadata
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title = soup.title.string.strip() if soup.title else ""

        # Extract main content - try different selectors for common content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.article-content',
            '[role="main"]',
            'body'
        ]

        content_text = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content_text = content_element.get_text(separator=' ', strip=True)
                if content_text and len(content_text) > 100:  # Ensure we have substantial content
                    break

        # If no content found with selectors, get from body
        if not content_text:
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator=' ', strip=True)

        # Clean up the content
        import re
        # Remove extra whitespace
        content_text = re.sub(r'\s+', ' ', content_text).strip()

        # Extract metadata
        metadata = {
            'url': url,
            'title': title,
            'content_length': len(content_text),
            'extracted_at': time.time()
        }

        # Try to extract additional metadata
        try:
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '')

            # Extract meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                metadata['keywords'] = meta_keywords.get('content', '')

            # Extract all headings
            headings = []
            for i in range(1, 7):  # h1 to h6
                for heading in soup.find_all(f'h{i}'):
                    headings.append({
                        'level': i,
                        'text': heading.get_text(strip=True)
                    })
            metadata['headings'] = headings

        except Exception as e:
            app_logger.warning(f"Error extracting additional metadata: {str(e)}")

        return {
            'content': content_text,
            'title': title,
            'metadata': metadata
        }

    def fetch_and_extract(self, url: str) -> BookContent:
        """
        Fetch content from URL and extract meaningful text.

        Args:
            url: URL to fetch and extract content from

        Returns:
            BookContent instance with extracted content
        """
        html_content = self.fetch_content(url)
        extracted_data = self.extract_content_from_html(html_content, url)

        # Generate unique ID for this content
        content_id = generate_content_id(url, extracted_data['content'])

        # Create BookContent instance
        book_content = BookContent.create(
            id=content_id,
            url=url,
            title=extracted_data['title'],
            content=extracted_data['content'],
            metadata=extracted_data['metadata']
        )

        app_logger.info(f"Successfully extracted content from {url}, ID: {content_id}")
        return book_content


# For command-line usage
def main():
    """Command-line interface for URL fetching."""
    import argparse

    parser = argparse.ArgumentParser(description='Fetch and extract content from URLs')
    parser.add_argument('--url', type=str, required=True, help='URL to fetch content from')
    args = parser.parse_args()

    try:
        fetcher = URLFetcher()
        content = fetcher.fetch_and_extract(args.url)
        print(f"Title: {content.title}")
        print(f"Content length: {len(content.content)} characters")
        print(f"Content ID: {content.id}")
    except Exception as e:
        app_logger.error(f"Error in command-line URL fetching: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()