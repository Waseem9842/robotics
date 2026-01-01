"""Module to orchestrate the content extraction pipeline."""

from typing import List, Dict, Any
from src.ingestion.url_fetcher import URLFetcher
from src.ingestion.text_processor import TextProcessor
from src.models.book_content import BookContent
from src.utils.logger import app_logger
from src.exceptions import ContentExtractionError
from src.config import Config


class ContentExtractionPipeline:
    """Class to orchestrate the full content extraction pipeline."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the content extraction pipeline.

        Args:
            chunk_size: Size of text chunks (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.url_fetcher = URLFetcher()
        self.text_processor = TextProcessor(
            chunk_size=chunk_size or Config.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or Config.CHUNK_OVERLAP
        )

    def extract_from_url(self, url: str) -> List[BookContent]:
        """
        Extract content from a single URL.

        Args:
            url: URL to extract content from

        Returns:
            List of BookContent instances (one for each chunk)
        """
        try:
            app_logger.info(f"Starting content extraction from URL: {url}")

            # Fetch and extract content
            book_content = self.url_fetcher.fetch_and_extract(url)

            # Process the content into chunks
            content_chunks = self.text_processor.process_with_validation(book_content.content)

            # Create BookContent instances for each chunk
            chunked_contents = []
            for i, chunk in enumerate(content_chunks):
                chunk_content = BookContent.create(
                    id=f"{book_content.id}_chunk_{i}",
                    url=book_content.url,
                    title=f"{book_content.title} - Chunk {i+1}",
                    content=chunk,
                    metadata={
                        **book_content.metadata,
                        'chunk_index': i,
                        'total_chunks': len(content_chunks),
                        'original_content_id': book_content.id
                    }
                )
                chunked_contents.append(chunk_content)

            app_logger.info(f"Successfully extracted {len(chunked_contents)} content chunks from {url}")
            return chunked_contents

        except Exception as e:
            app_logger.error(f"Error extracting content from {url}: {str(e)}")
            raise ContentExtractionError(f"Failed to extract content from {url}: {str(e)}")

    def extract_from_urls(self, urls: List[str]) -> List[BookContent]:
        """
        Extract content from multiple URLs.

        Args:
            urls: List of URLs to extract content from

        Returns:
            List of BookContent instances
        """
        all_contents = []
        for url in urls:
            try:
                contents = self.extract_from_url(url)
                all_contents.extend(contents)
            except Exception as e:
                app_logger.error(f"Skipping URL {url} due to error: {str(e)}")
                # Continue with other URLs
                continue

        app_logger.info(f"Completed extraction from {len(urls)} URLs, got {len(all_contents)} content chunks")
        return all_contents

    def run(self, urls: List[str]) -> Dict[str, Any]:
        """
        Run the full content extraction pipeline.

        Args:
            urls: List of URLs to process

        Returns:
            Dictionary with results and statistics
        """
        app_logger.info(f"Starting content extraction pipeline for {len(urls)} URLs")

        try:
            contents = self.extract_from_urls(urls)

            # Generate statistics
            stats = {
                'total_urls_processed': len(urls),
                'total_content_chunks': len(contents),
                'average_chunk_length': sum(len(c.content) for c in contents) / len(contents) if contents else 0,
                'successful_extractions': len([c for c in contents if c.content.strip()]),
                'failed_extractions': len([c for c in contents if not c.content.strip()])
            }

            app_logger.info(f"Pipeline completed successfully. Stats: {stats}")
            return {
                'contents': contents,
                'stats': stats
            }

        except Exception as e:
            app_logger.error(f"Pipeline failed: {str(e)}")
            raise ContentExtractionError(f"Content extraction pipeline failed: {str(e)}")


# For command-line usage
def main():
    """Command-line interface for the content extraction pipeline."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Content extraction pipeline')
    parser.add_argument('--urls', nargs='+', required=True, help='URLs to extract content from')
    args = parser.parse_args()

    try:
        pipeline = ContentExtractionPipeline()
        result = pipeline.run(args.urls)

        print(f"Extraction completed!")
        print(f"Total content chunks: {result['stats']['total_content_chunks']}")
        print(f"Average chunk length: {result['stats']['average_chunk_length']:.2f}")
        print(f"Successful extractions: {result['stats']['successful_extractions']}")
    except Exception as e:
        app_logger.error(f"Error in command-line content extraction: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()