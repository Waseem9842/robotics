import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path to import retrieve module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.retrieve import RetrievalValidator


class TestQdrantSearchIntegration:
    """Integration tests for Qdrant search functionality"""

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_search_similar_chunks_success(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test successful similarity search"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "test_id"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "text": "test text content",
            "metadata": {"source": "test_source"},
            "source_url": "http://example.com"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method
        query = "test query"
        collection_name = "test_collection"
        result = validator.search_similar_chunks(query, collection_name, top_k=1, threshold=0.5)

        # Assertions
        assert len(result) == 1
        assert result[0]["id"] == "test_id"
        assert result[0]["text"] == "test text content"
        assert result[0]["score"] == 0.9
        assert result[0]["metadata"]["source"] == "test_source"
        assert result[0]["source_url"] == "http://example.com"

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_search_similar_chunks_empty_result(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test similarity search with no results"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = []
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method
        query = "test query"
        collection_name = "test_collection"
        result = validator.search_similar_chunks(query, collection_name, top_k=5, threshold=0.5)

        # Assertions
        assert len(result) == 0