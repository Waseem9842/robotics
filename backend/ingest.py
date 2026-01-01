"""
Data Ingestion Module for RAG System

This module crawls the provided website and ingests content into Qdrant for RAG retrieval.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
import dotenv
import logging
from typing import List, Dict, Any
import uuid


class DataIngestor:
    """
    Ingests website content into Qdrant for RAG retrieval.
    """

    def __init__(self, qdrant_url: str, qdrant_api_key: str, cohere_api_key: str, collection_name: str = "robotics_docs"):
        """
        Initialize the data ingestor with Qdrant and Cohere clients.

        Args:
            qdrant_url: URL for Qdrant instance
            qdrant_api_key: API key for Qdrant
            cohere_api_key: API key for Cohere
            collection_name: Name of the Qdrant collection to store documents
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize clients
        try:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            self.cohere_client = cohere.Client(cohere_api_key)
            self.collection_name = collection_name
            self.logger.info("Successfully initialized Qdrant and Cohere clients")
        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {str(e)}")
            raise

        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        """
        Create the Qdrant collection if it doesn't exist.
        """
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection with vector configuration
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),  # Cohere embedding size
                )
                self.logger.info(f"Created collection: {self.collection_name}")
            else:
                self.logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            self.logger.error(f"Failed to create collection: {str(e)}")
            raise

    def extract_text_from_url(self, url: str) -> str:
        """
        Extract text content from a given URL.

        Args:
            url: The URL to extract text from

        Returns:
            Extracted text content
        """
        try:
            self.logger.info(f"Extracting text from URL: {url}")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; DataIngestor/1.0)'})
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except Exception as e:
            self.logger.error(f"Failed to extract text from {url}: {str(e)}")
            return ""

    def get_urls_from_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Extract URLs from a sitemap.xml file.

        Args:
            sitemap_url: URL to the sitemap.xml file

        Returns:
            List of URLs extracted from the sitemap
        """
        try:
            self.logger.info(f"Extracting URLs from sitemap: {sitemap_url}")
            response = requests.get(sitemap_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'xml')
            urls = []

            # Look for <url><loc> elements in sitemap
            for url_element in soup.find_all('loc'):
                urls.append(url_element.text.strip())

            # If no URLs found, try looking for <url> elements
            if not urls:
                for url_element in soup.find_all('url'):
                    loc_element = url_element.find('loc')
                    if loc_element:
                        urls.append(loc_element.text.strip())

            self.logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
        except Exception as e:
            self.logger.error(f"Failed to parse sitemap {sitemap_url}: {str(e)}")
            return []

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start forward by chunk_size minus overlap
            start = end - overlap

            # If remaining text is less than chunk_size, add it as final chunk
            if start + chunk_size > len(text):
                if start < len(text):
                    chunks.append(text[start:])
                break

        return chunks

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using Cohere.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            self.logger.debug(f"Generating embedding for text: {text[:50]}...")
            response = self.cohere_client.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_document"  # Specify the input type
            )
            embedding = response.embeddings[0]
            self.logger.debug(f"Successfully generated embedding with length: {len(embedding)}")
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to generate embedding for text: {str(e)}")
            raise

    def ingest_url(self, url: str, max_chunk_size: int = 1000):
        """
        Ingest content from a single URL into Qdrant.

        Args:
            url: The URL to ingest
            max_chunk_size: Maximum size of text chunks
        """
        try:
            # Extract text from URL
            text = self.extract_text_from_url(url)
            if not text.strip():
                self.logger.warning(f"No text extracted from {url}")
                return

            # Chunk the text
            text_chunks = self.chunk_text(text, chunk_size=max_chunk_size, overlap=100)
            self.logger.info(f"Chunked content from {url} into {len(text_chunks)} chunks")

            # Process each chunk
            points = []
            for i, chunk in enumerate(text_chunks):
                if not chunk.strip():
                    continue

                # Generate embedding
                embedding = self.get_embedding(chunk)

                # Create Qdrant point
                point_id = str(uuid.uuid4())  # Generate a proper UUID for Qdrant
                point = models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "source_url": url,
                        "chunk_index": i,
                        "metadata": {
                            "source": "robotics_hackathon_docs",
                            "type": "webpage_content"
                        }
                    }
                )
                points.append(point)

            # Upload points to Qdrant
            if points:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                self.logger.info(f"Successfully ingested {len(points)} chunks from {url}")
            else:
                self.logger.warning(f"No valid chunks to ingest from {url}")
        except Exception as e:
            self.logger.error(f"Failed to ingest URL {url}: {str(e)}")

    def ingest_sitemap(self, sitemap_url: str, max_chunk_size: int = 1000):
        """
        Ingest all URLs from a sitemap into Qdrant.

        Args:
            sitemap_url: URL to the sitemap.xml file
            max_chunk_size: Maximum size of text chunks
        """
        # Get URLs from sitemap
        urls = self.get_urls_from_sitemap(sitemap_url)

        if not urls:
            self.logger.warning("No URLs found in sitemap")
            return

        # Ingest each URL
        for i, url in enumerate(urls):
            self.logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            self.ingest_url(url, max_chunk_size=max_chunk_size)

        self.logger.info(f"Completed ingestion of {len(urls)} URLs from sitemap")


def url_hash(url: str) -> str:
    """
    Generate a simple hash for a URL to use as a point ID.
    """
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()


def main():
    """
    Main function to run the data ingestion from command line.
    """
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        logger.info("Starting data ingestion process")

        # Load environment variables
        dotenv.load_dotenv()

        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        cohere_api_key = os.getenv("COHERE_API_KEY")

        if not all([qdrant_url, qdrant_api_key, cohere_api_key]):
            error_msg = "Missing required environment variables. Please set QDRANT_URL, QDRANT_API_KEY, and COHERE_API_KEY"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Initialize ingestor
        logger.info("Initializing data ingestor...")
        ingestor = DataIngestor(qdrant_url, qdrant_api_key, cohere_api_key)

        # Sitemap URL for the robotics website
        sitemap_url = "https://robotics-hackathone.vercel.app/sitemap.xml"

        # Perform ingestion
        logger.info(f"Starting ingestion from sitemap: {sitemap_url}")
        ingestor.ingest_sitemap(sitemap_url)

        logger.info("Data ingestion completed successfully!")
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        raise


if __name__ == "__main__":
    main()