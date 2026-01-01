import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path to import retrieve module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.retrieve import RetrievalValidator


class TestDataIntegrityIntegration:
    """Integration tests for data integrity validation"""

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_complete_content(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with complete content (data integrity passes)"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "id1"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "text": "Complete text content",
            "metadata": {"source": "source1", "type": "document"},
            "source_url": "http://example.com/source1"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["data_integrity_check"] is True
        assert result["validation_passed"] is True
        assert len(result["retrieved_chunks"]) == 1
        assert result["retrieved_chunks"][0]["text"] == "Complete text content"

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_missing_content(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with missing content (data integrity fails)"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "id1"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "text": "",  # Missing text content
            "metadata": {"source": "source1"},
            "source_url": "http://example.com/source1"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["data_integrity_check"] is False
        assert result["validation_passed"] is True  # Validation passes but data integrity fails
        assert len(result["retrieved_chunks"]) == 1
        assert result["retrieved_chunks"][0]["text"] == ""

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_missing_source_url(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with missing source URL (data integrity fails)"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "id1"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "text": "Complete text content",
            "metadata": {"source": "source1"},
            "source_url": ""  # Missing source URL
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["data_integrity_check"] is False
        assert result["validation_passed"] is True  # Validation passes but data integrity fails
        assert len(result["retrieved_chunks"]) == 1
        assert result["retrieved_chunks"][0]["text"] == "Complete text content"

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_missing_metadata(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with missing metadata (data integrity fails)"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "id1"
        mock_search_result.score = 0.9
        mock_search_result.payload = {
            "text": "Complete text content",
            "metadata": None,  # Missing metadata
            "source_url": "http://example.com/source1"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["data_integrity_check"] is False
        assert result["validation_passed"] is True  # Validation passes but data integrity fails
        assert len(result["retrieved_chunks"]) == 1
        assert result["retrieved_chunks"][0]["text"] == "Complete text content"

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_multiple_chunks_mixed_integrity(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with multiple chunks where one has missing content"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result1 = Mock()
        mock_search_result1.id = "id1"
        mock_search_result1.score = 0.9
        mock_search_result1.payload = {
            "text": "Complete text content",
            "metadata": {"source": "source1"},
            "source_url": "http://example.com/source1"
        }
        mock_search_result2 = Mock()
        mock_search_result2.id = "id2"
        mock_search_result2.score = 0.7
        mock_search_result2.payload = {
            "text": "",  # Missing text content
            "metadata": {"source": "source2"},
            "source_url": "http://example.com/source2"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result1, mock_search_result2]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["data_integrity_check"] is False  # Because one chunk has missing text
        assert result["validation_passed"] is True  # Validation passes but data integrity fails
        assert len(result["retrieved_chunks"]) == 2