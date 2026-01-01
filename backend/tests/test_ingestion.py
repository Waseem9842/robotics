"""Tests for ingestion functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ingestion.url_fetcher import URLFetcher, generate_content_id
from src.ingestion.text_processor import TextProcessor
from src.ingestion.pipeline import ContentExtractionPipeline
from src.models.book_content import BookContent
import requests


class TestURLFetcher:
    """Test cases for URLFetcher class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.fetcher = URLFetcher()

    def test_fetch_content_success(self):
        """Test successful content fetching."""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body>Test content</body></html>'
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = self.fetcher.fetch_content('https://example.com')
            assert result == '<html><body>Test content</body></html>'
            mock_get.assert_called_once()

    def test_fetch_content_request_exception(self):
        """Test content fetching with request exception."""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Connection error")

            with pytest.raises(Exception):
                self.fetcher.fetch_content('https://example.com')

    def test_extract_content_from_html(self):
        """Test extracting content from HTML."""
        html_content = '''
        <html>
            <head><title>Test Title</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>This is test content.</p>
                <div class="content">More content here.</div>
            </body>
        </html>
        '''
        result = self.fetcher.extract_content_from_html(html_content, 'https://example.com')

        assert 'Test Title' in result['title']
        assert 'test content' in result['content'].lower()
        assert 'more content here' in result['content'].lower()
        assert result['metadata']['url'] == 'https://example.com'

    def test_fetch_and_extract(self):
        """Test the complete fetch and extract process."""
        with patch.object(self.fetcher, 'fetch_content') as mock_fetch:
            mock_fetch.return_value = '<html><head><title>Test</title></head><body>Content</body></html>'

            result = self.fetcher.fetch_and_extract('https://example.com')

            assert isinstance(result, BookContent)
            assert result.title == 'Test'
            assert result.content == 'Content'
            assert result.url == 'https://example.com'


class TestTextProcessor:
    """Test cases for TextProcessor class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = TextProcessor(chunk_size=100, chunk_overlap=10)

    def test_clean(self):
        """Test text cleaning."""
        dirty_text = "  This   is  \n\ta  test   text  \t\n  "
        cleaned = self.processor.clean(dirty_text)
        assert cleaned == "This is a test text"

    def test_chunk(self):
        """Test text chunking."""
        text = "This is a sample text for chunking. " * 10  # Create a longer text
        chunks = self.processor.chunk(text)
        assert len(chunks) > 0
        assert all(len(chunk) <= 100 for chunk in chunks)

    def test_process(self):
        """Test the complete text processing."""
        text = "This is a sample text for processing. " * 5
        chunks = self.processor.process(text)
        assert len(chunks) > 0

    def test_validate_chunk(self):
        """Test chunk validation."""
        # Valid chunk
        assert self.processor.validate_chunk("This is a valid chunk")

        # Invalid chunks
        assert not self.processor.validate_chunk("")
        assert not self.processor.validate_chunk("   ")
        assert not self.processor.validate_chunk("ab")  # Too short


class TestContentExtractionPipeline:
    """Test cases for ContentExtractionPipeline class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.pipeline = ContentExtractionPipeline(chunk_size=100, chunk_overlap=10)

    @patch('src.ingestion.url_fetcher.URLFetcher.fetch_and_extract')
    def test_extract_from_url(self, mock_fetch_extract):
        """Test extracting from a single URL."""
        mock_content = BookContent.create(
            id='test_id',
            url='https://example.com',
            title='Test Title',
            content='This is test content. ' * 5,
            metadata={'test': 'metadata'}
        )
        mock_fetch_extract.return_value = mock_content

        result = self.pipeline.extract_from_url('https://example.com')
        assert len(result) > 0
        assert all(isinstance(content, BookContent) for content in result)

    def test_extract_from_urls(self):
        """Test extracting from multiple URLs."""
        with patch.object(self.pipeline, 'extract_from_url') as mock_extract:
            mock_content = BookContent.create(
                id='test_id',
                url='https://example.com',
                title='Test Title',
                content='Test content',
                metadata={}
            )
            mock_extract.return_value = [mock_content]

            result = self.pipeline.extract_from_urls(['https://example.com', 'https://example2.com'])
            assert len(result) == 2

    @patch('src.ingestion.url_fetcher.URLFetcher.fetch_and_extract')
    def test_run_pipeline(self, mock_fetch_extract):
        """Test running the full pipeline."""
        mock_content = BookContent.create(
            id='test_id',
            url='https://example.com',
            title='Test Title',
            content='This is test content. ' * 3,
            metadata={'test': 'metadata'}
        )
        mock_fetch_extract.return_value = mock_content

        result = self.pipeline.run(['https://example.com'])

        assert 'contents' in result
        assert 'stats' in result
        assert result['stats']['total_urls_processed'] == 1
        assert result['stats']['total_content_chunks'] > 0


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__])