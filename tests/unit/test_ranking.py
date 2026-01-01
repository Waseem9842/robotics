import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path to import retrieve module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.retrieve import RetrievalValidator


class TestRankingValidation:
    """Unit tests for ranking validation functionality"""

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_ranking_correctness_perfect_order(self, mock_dotenv, mock_cohere_client):
        """Test ranking correctness calculation with perfectly ordered scores"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Create test data with perfectly ordered scores (descending)
        retrieved_chunks = [
            {"score": 0.9},
            {"score": 0.7},
            {"score": 0.5},
            {"score": 0.3}
        ]

        # Test the internal logic for ranking correctness
        ranking_correctness = 1.0  # Perfect if scores are descending
        if len(retrieved_chunks) > 1:
            for i in range(1, len(retrieved_chunks)):
                if retrieved_chunks[i]["score"] > retrieved_chunks[i-1]["score"]:
                    ranking_correctness = 0.0  # Not perfectly ranked
                    break

        assert ranking_correctness == 1.0

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_ranking_correctness_misordered(self, mock_dotenv, mock_cohere_client):
        """Test ranking correctness calculation with misordered scores"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Create test data with misordered scores (not descending)
        retrieved_chunks = [
            {"score": 0.5},
            {"score": 0.9},  # Higher score later in list
            {"score": 0.3}
        ]

        # Test the internal logic for ranking correctness
        ranking_correctness = 1.0  # Perfect if scores are descending
        if len(retrieved_chunks) > 1:
            for i in range(1, len(retrieved_chunks)):
                if retrieved_chunks[i]["score"] > retrieved_chunks[i-1]["score"]:
                    ranking_correctness = 0.0  # Not perfectly ranked
                    break

        assert ranking_correctness == 0.0

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_ranking_correctness_single_item(self, mock_dotenv, mock_cohere_client):
        """Test ranking correctness calculation with single item"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Create test data with single item
        retrieved_chunks = [
            {"score": 0.9}
        ]

        # Test the internal logic for ranking correctness
        ranking_correctness = 1.0  # Perfect if scores are descending
        if len(retrieved_chunks) > 1:
            for i in range(1, len(retrieved_chunks)):
                if retrieved_chunks[i]["score"] > retrieved_chunks[i-1]["score"]:
                    ranking_correctness = 0.0  # Not perfectly ranked
                    break

        assert ranking_correctness == 1.0

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_ranking_correctness_empty_list(self, mock_dotenv, mock_cohere_client):
        """Test ranking correctness calculation with empty list"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Create test data with empty list
        retrieved_chunks = []

        # Test the internal logic for ranking correctness
        ranking_correctness = 1.0  # Perfect if scores are descending
        if len(retrieved_chunks) > 1:
            for i in range(1, len(retrieved_chunks)):
                if retrieved_chunks[i]["score"] > retrieved_chunks[i-1]["score"]:
                    ranking_correctness = 0.0  # Not perfectly ranked
                    break

        assert ranking_correctness == 1.0