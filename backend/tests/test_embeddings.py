"""Tests for embedding functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.embeddings.cohere_client import CohereClient
from src.embeddings.generator import EmbeddingGenerator
from src.models.book_content import BookContent
from src.models.embedding_vector import EmbeddingVector


class TestCohereClient:
    """Test cases for CohereClient class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with patch('cohere.Client'):
            self.client = CohereClient(api_key='test_key')

    def test_generate_single_embedding(self):
        """Test generating a single embedding."""
        with patch.object(self.client, 'generate_embeddings') as mock_gen:
            mock_gen.return_value = [[0.1, 0.2, 0.3]]

            result = self.client.generate_single_embedding("test text")
            assert result == [0.1, 0.2, 0.3]
            mock_gen.assert_called_once_with(["test text"], "embed-english-v3.0", "search_document")

    def test_generate_embeddings(self):
        """Test generating multiple embeddings."""
        with patch.object(self.client.client, 'embed') as mock_embed:
            mock_embed.return_value = Mock()
            mock_embed.return_value.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

            result = self.client.generate_embeddings(["text1", "text2"])
            assert len(result) == 2
            assert result[0] == [0.1, 0.2, 0.3]

    def test_empty_texts(self):
        """Test generating embeddings for empty texts."""
        result = self.client.generate_embeddings([])
        assert result == []

    def test_validate_api_connection(self):
        """Test API connection validation."""
        with patch.object(self.client, 'generate_single_embedding') as mock_gen:
            mock_gen.return_value = [0.1, 0.2, 0.3]

            result = self.client.validate_api_connection()
            assert result is True


class TestEmbeddingGenerator:
    """Test cases for EmbeddingGenerator class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with patch('cohere.Client'):
            self.generator = EmbeddingGenerator(cohere_api_key='test_key')

    def test_generate_from_text(self):
        """Test generating embedding from text."""
        with patch.object(self.generator.cohere_client, 'generate_single_embedding') as mock_gen:
            mock_gen.return_value = [0.1, 0.2, 0.3, 0.4]

            result = self.generator.generate_from_text("test text")
            assert isinstance(result, EmbeddingVector)
            assert result.vector == [0.1, 0.2, 0.3, 0.4]

    def test_generate_from_content(self):
        """Test generating embedding from BookContent."""
        content = BookContent.create(
            id='test_id',
            url='https://example.com',
            title='Test Title',
            content='This is test content',
            metadata={}
        )

        with patch.object(self.generator.cohere_client, 'generate_single_embedding') as mock_gen:
            mock_gen.return_value = [0.1, 0.2, 0.3, 0.4]

            result = self.generator.generate_from_content(content)
            assert isinstance(result, EmbeddingVector)
            assert result.vector == [0.1, 0.2, 0.3, 0.4]
            assert result.content_id == 'test_id'

    def test_generate_batch_from_texts(self):
        """Test generating embeddings for a batch of texts."""
        texts = ["text1", "text2", "text3"]

        with patch.object(self.generator.cohere_client, 'generate_embeddings') as mock_gen:
            mock_gen.return_value = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

            result = self.generator.generate_batch_from_texts(texts)
            assert len(result) == 3
            assert all(isinstance(emb, EmbeddingVector) for emb in result)

    def test_generate_batch_from_contents(self):
        """Test generating embeddings for a batch of contents."""
        contents = [
            BookContent.create(
                id='id1',
                url='https://example1.com',
                title='Title 1',
                content='Content 1',
                metadata={}
            ),
            BookContent.create(
                id='id2',
                url='https://example2.com',
                title='Title 2',
                content='Content 2',
                metadata={}
            )
        ]

        with patch.object(self.generator.cohere_client, 'generate_embeddings') as mock_gen:
            mock_gen.return_value = [[0.1, 0.2], [0.3, 0.4]]

            result = self.generator.generate_batch_from_contents(contents)
            assert len(result) == 2
            assert all(isinstance(emb, EmbeddingVector) for emb in result)
            assert result[0].content_id == 'id1'
            assert result[1].content_id == 'id2'

    def test_validate_embedding(self):
        """Test embedding validation."""
        # Valid embedding
        valid_embedding = EmbeddingVector.create(
            id='test_id',
            vector=[0.1, 0.2, 0.3, 0.4, 0.5],
            content_id='content_id',
            model_name='test_model'
        )
        assert self.generator.validate_embedding(valid_embedding) is True

        # Invalid embedding (all zeros)
        zero_embedding = EmbeddingVector.create(
            id='test_id',
            vector=[0.0, 0.0, 0.0, 0.0],
            content_id='content_id',
            model_name='test_model'
        )
        assert self.generator.validate_embedding(zero_embedding) is False

        # Invalid embedding (too short)
        short_embedding = EmbeddingVector.create(
            id='test_id',
            vector=[0.1],
            content_id='content_id',
            model_name='test_model'
        )
        assert self.generator.validate_embedding(short_embedding) is False

        # Invalid embedding (NaN values)
        import math
        nan_embedding = EmbeddingVector.create(
            id='test_id',
            vector=[0.1, math.nan, 0.3],
            content_id='content_id',
            model_name='test_model'
        )
        assert self.generator.validate_embedding(nan_embedding) is False

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Empty text
        with pytest.raises(Exception):
            self.generator.generate_from_text("")

        # Empty contents list
        result = self.generator.generate_batch_from_contents([])
        assert result == []

        # Empty texts list
        result = self.generator.generate_batch_from_texts([])
        assert result == []


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__])