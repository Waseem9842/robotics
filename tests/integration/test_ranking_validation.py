import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path to import retrieve module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.retrieve import RetrievalValidator


class TestRankingValidationIntegration:
    """Integration tests for ranking correctness validation"""

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_perfect_ranking(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with perfectly ranked results"""
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
            "text": "text1",
            "metadata": {"source": "source1"},
            "source_url": "url1"
        }
        mock_search_result2 = Mock()
        mock_search_result2.id = "id2"
        mock_search_result2.score = 0.7
        mock_search_result2.payload = {
            "text": "text2",
            "metadata": {"source": "source2"},
            "source_url": "url2"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result1, mock_search_result2]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["ranking_correctness"] == 1.0  # Perfect ranking (scores in descending order)
        assert result["validation_passed"] is True
        assert len(result["retrieved_chunks"]) == 2

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_misordered_ranking(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with misordered ranking"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result1 = Mock()
        mock_search_result1.id = "id1"
        mock_search_result1.score = 0.5  # Lower score first
        mock_search_result1.payload = {
            "text": "text1",
            "metadata": {"source": "source1"},
            "source_url": "url1"
        }
        mock_search_result2 = Mock()
        mock_search_result2.id = "id2"
        mock_search_result2.score = 0.9  # Higher score second
        mock_search_result2.payload = {
            "text": "text2",
            "metadata": {"source": "source2"},
            "source_url": "url2"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result1, mock_search_result2]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["ranking_correctness"] == 0.0  # Not perfectly ranked
        assert result["validation_passed"] is True
        assert len(result["retrieved_chunks"]) == 2

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_with_single_result(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with single result (always perfectly ranked)"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "id1"
        mock_search_result.score = 0.8
        mock_search_result.payload = {
            "text": "text1",
            "metadata": {"source": "source1"},
            "source_url": "url1"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Perform validation
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["ranking_correctness"] == 1.0  # Single item is always perfectly ranked
        assert result["validation_passed"] is True
        assert len(result["retrieved_chunks"]) == 1