import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path to import retrieve module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.retrieve import RetrievalValidator


class TestEdgeCases:
    """Unit tests for edge cases in the retrieval validation"""

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_get_embedding_empty_text(self, mock_dotenv, mock_cohere_client):
        """Test embedding generation with empty text"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method with empty text
        result = validator.get_embedding("")

        # Assertions
        assert result == []
        mock_cohere_instance.embed.assert_called_once_with(
            texts=[""],
            model="embed-english-v3.0"
        )

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_get_embedding_whitespace_text(self, mock_dotenv, mock_cohere_client):
        """Test embedding generation with whitespace text"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.0, 0.0, 0.0]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method with whitespace text
        result = validator.get_embedding("   ")

        # Assertions
        assert result == [0.0, 0.0, 0.0]
        mock_cohere_instance.embed.assert_called_once_with(
            texts=["   "],
            model="embed-english-v3.0"
        )

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_search_similar_chunks_empty_results(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test similarity search with no results returned"""
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
        result = validator.search_similar_chunks("test query", "test_collection", top_k=5, threshold=0.7)

        # Assertions
        assert result == []
        assert len(result) == 0

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_search_similar_chunks_single_result(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test similarity search with single result"""
        # Setup mocks
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        mock_qdrant_instance = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "single_id"
        mock_search_result.score = 0.85
        mock_search_result.payload = {
            "text": "single result text",
            "metadata": {"source": "test"},
            "source_url": "http://example.com"
        }
        mock_qdrant_instance.search.return_value = [mock_search_result]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method
        result = validator.search_similar_chunks("test query", "test_collection", top_k=1, threshold=0.5)

        # Assertions
        assert len(result) == 1
        assert result[0]["id"] == "single_id"
        assert result[0]["score"] == 0.85
        assert result[0]["text"] == "single result text"

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_calculate_ranking_metrics_empty_list(self, mock_dotenv, mock_cohere_client):
        """Test ranking metrics calculation with empty list"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method with empty list
        result = validator.calculate_ranking_metrics([])

        # Assertions
        assert result["ranking_correctness"] == 1.0
        assert result["normalized_discounted_cumulative_gain"] == 1.0
        assert result["mean_reciprocal_rank"] == 1.0
        assert result["precision_at_k"] == 0.0  # 0 if no results

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_calculate_ranking_metrics_single_item(self, mock_dotenv, mock_cohere_client):
        """Test ranking metrics calculation with single item"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method with single item
        retrieved_chunks = [{"score": 0.8}]
        result = validator.calculate_ranking_metrics(retrieved_chunks)

        # Assertions
        assert result["ranking_correctness"] == 1.0
        assert result["normalized_discounted_cumulative_gain"] == 1.0
        assert result["mean_reciprocal_rank"] == 1.0
        assert result["precision_at_k"] == 1.0

    @patch('backend.retrieve.QdrantClient')
    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_validate_retrieval_empty_results(self, mock_dotenv, mock_cohere_client, mock_qdrant_client):
        """Test validation with empty results"""
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
        result = validator.validate_retrieval("test query", "test_collection")

        # Assertions
        assert result["validation_passed"] is False  # No results means validation failed
        assert result["accuracy_score"] == 0.0
        assert result["retrieved_chunks"] == []
        assert result["data_integrity_check"] is True  # True because no chunks to check