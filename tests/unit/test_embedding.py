import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path to import retrieve module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.retrieve import RetrievalValidator


class TestEmbeddingGeneration:
    """Unit tests for embedding generation functionality"""

    @patch('backend.retrieve.cohere.Client')
    @patch('backend.retrieve.dotenv')
    def test_get_embedding_success(self, mock_dotenv, mock_cohere_client):
        """Test successful embedding generation"""
        # Setup mock
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock()
        mock_cohere_instance.embed.return_value.embeddings = [[0.1, 0.2, 0.3]]
        mock_cohere_client.return_value = mock_cohere_instance

        # Initialize validator
        validator = RetrievalValidator("test_url", "test_key", "test_key")

        # Call method
        text = "test query"
        result = validator.get_embedding(text)

        # Assertions
        assert result == [0.1, 0.2, 0.3]
        mock_cohere_instance.embed.assert_called_once_with(
            texts=[text],
            model="embed-english-v3.0"
        )

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