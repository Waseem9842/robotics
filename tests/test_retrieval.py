import pytest
from unittest.mock import Mock, patch
from src.qdrant_client import QdrantClientUtility, retrieve_context_for_question


class TestQdrantRetrieval:
    """
    Integration tests for Qdrant retrieval functionality
    """

    @patch('src.qdrant_client.QdrantClient')
    @patch('openai.OpenAI')  # Fixed import path
    def test_qdrant_client_search(self, mock_openai_class, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the OpenAI client and embedding response
        mock_openai_instance = Mock()
        mock_openai_class.return_value = mock_openai_instance

        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock()]
        mock_embedding_response.data[0].embedding = [0.1, 0.2, 0.3]  # Mock embedding
        mock_openai_instance.embeddings.create.return_value = mock_embedding_response

        # Mock the search result
        mock_hit = Mock()
        mock_hit.payload = {"content": "Test document content", "source": "test_source"}
        mock_hit.score = 0.8
        mock_hit.id = "test_id"
        mock_client_instance.search.return_value = [mock_hit]

        # Act
        client_utility = QdrantClientUtility()
        result = client_utility.search("test query")

        # Assert
        assert len(result) == 1
        assert result[0]["content"] == "Test document content"
        assert result[0]["score"] == 0.8
        mock_client_instance.search.assert_called_once()

    @patch('src.qdrant_client.QdrantClientUtility.search')
    def test_retrieve_context_for_question(self, mock_search):
        # Arrange
        mock_search.return_value = [
            {
                "content": "Test context content",
                "metadata": {"source": "test_source"},
                "score": 0.8,
                "source_documents": ["test_id"]
            }
        ]

        # Act
        result = retrieve_context_for_question("test question")

        # Assert
        assert len(result) == 1
        assert result[0]["content"] == "Test context content"
        mock_search.assert_called_once()

    def test_qdrant_client_initialization(self):
        # Act
        client_utility = QdrantClientUtility()

        # Assert
        assert client_utility is not None
        assert hasattr(client_utility, 'client')


if __name__ == "__main__":
    pytest.main([__file__])