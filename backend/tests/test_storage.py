"""Tests for vector storage functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.storage.qdrant_client import QdrantClientWrapper
from src.storage.vector_store import VectorStore
from src.models.embedding_vector import EmbeddingVector
from src.models.book_content import BookContent
from src.models.vector_record import VectorRecord


class TestQdrantClient:
    """Test cases for QdrantClientWrapper class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with patch('qdrant_client.QdrantClient'):
            self.client = QdrantClientWrapper(
                api_key='test_key',
                host='https://test.qdrant.io',
                collection_name='test_collection'
            )

    def test_create_collection(self):
        """Test creating a collection."""
        with patch.object(self.client.client, 'get_collections') as mock_get_coll:
            mock_get_coll.return_value = Mock()
            mock_get_coll.return_value.collections = []

            with patch.object(self.client.client, 'create_collection') as mock_create:
                result = self.client.create_collection()
                assert result is True
                mock_create.assert_called_once()

    def test_store_vector(self):
        """Test storing a single vector."""
        with patch.object(self.client, 'create_collection') as mock_create_coll:
            mock_create_coll.return_value = True

            with patch.object(self.client.client, 'upsert') as mock_upsert:
                result = self.client.store_vector(
                    vector_id='test_id',
                    vector=[0.1, 0.2, 0.3],
                    payload={'test': 'data'}
                )
                assert result is True
                mock_upsert.assert_called_once()

    def test_store_vectors(self):
        """Test storing multiple vectors."""
        with patch.object(self.client, 'create_collection') as mock_create_coll:
            mock_create_coll.return_value = True

            with patch.object(self.client.client, 'upsert') as mock_upsert:
                result = self.client.store_vectors(
                    vector_ids=['id1', 'id2'],
                    vectors=[[0.1, 0.2], [0.3, 0.4]],
                    payloads=[{'test': 'data1'}, {'test': 'data2'}]
                )
                assert result is True
                mock_upsert.assert_called_once()

    def test_retrieve_vector(self):
        """Test retrieving a single vector."""
        mock_point = Mock()
        mock_point.id = 'test_id'
        mock_point.vector = [0.1, 0.2, 0.3]
        mock_point.payload = {'test': 'data'}

        with patch.object(self.client.client, 'retrieve') as mock_retrieve:
            mock_retrieve.return_value = [mock_point]

            result = self.client.retrieve_vector('test_id')
            assert result is not None
            assert result['id'] == 'test_id'
            assert result['vector'] == [0.1, 0.2, 0.3]
            assert result['payload'] == {'test': 'data'}

    def test_search_vectors(self):
        """Test searching for similar vectors."""
        mock_result = Mock()
        mock_result.id = 'test_id'
        mock_result.vector = [0.1, 0.2, 0.3]
        mock_result.payload = {'test': 'data'}
        mock_result.score = 0.9

        with patch.object(self.client.client, 'search') as mock_search:
            mock_search.return_value = [mock_result]

            results = self.client.search_vectors([0.1, 0.2, 0.3])
            assert len(results) == 1
            assert results[0]['id'] == 'test_id'
            assert results[0]['score'] == 0.9


class TestVectorStore:
    """Test cases for VectorStore class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with patch('qdrant_client.QdrantClient'):
            self.store = VectorStore(
                api_key='test_key',
                host='https://test.qdrant.io',
                collection_name='test_collection'
            )

    def test_store_embedding(self):
        """Test storing a single embedding."""
        embedding = EmbeddingVector.create(
            id='test_id',
            vector=[0.1, 0.2, 0.3],
            content_id='content_id',
            model_name='test_model'
        )

        content = BookContent.create(
            id='content_id',
            url='https://example.com',
            title='Test Title',
            content='Test content',
            metadata={}
        )

        with patch.object(self.store.qdrant_client, 'store_vector') as mock_store:
            mock_store.return_value = True

            result = self.store.store_embedding(embedding, content)
            assert result is True
            mock_store.assert_called_once()

    def test_store_embeddings(self):
        """Test storing multiple embeddings."""
        embeddings = [
            EmbeddingVector.create(
                id='id1',
                vector=[0.1, 0.2],
                content_id='content1',
                model_name='test_model'
            ),
            EmbeddingVector.create(
                id='id2',
                vector=[0.3, 0.4],
                content_id='content2',
                model_name='test_model'
            )
        ]

        contents = [
            BookContent.create(
                id='content1',
                url='https://example1.com',
                title='Title 1',
                content='Content 1',
                metadata={}
            ),
            BookContent.create(
                id='content2',
                url='https://example2.com',
                title='Title 2',
                content='Content 2',
                metadata={}
            )
        ]

        with patch.object(self.store.qdrant_client, 'store_vectors') as mock_store:
            mock_store.return_value = True

            result = self.store.store_embeddings(embeddings, contents)
            assert result is True
            mock_store.assert_called_once()

    def test_retrieve_embedding(self):
        """Test retrieving a single embedding."""
        mock_result = {
            'id': 'test_id',
            'vector': [0.1, 0.2, 0.3],
            'payload': {
                'content_id': 'content_id',
                'model_name': 'test_model'
            }
        }

        with patch.object(self.store.qdrant_client, 'retrieve_vector') as mock_retrieve:
            mock_retrieve.return_value = mock_result

            result = self.store.retrieve_embedding('test_id')
            assert isinstance(result, EmbeddingVector)
            assert result.id == 'test_id'
            assert result.vector == [0.1, 0.2, 0.3]
            assert result.content_id == 'content_id'

    def test_retrieve_embeddings(self):
        """Test retrieving multiple embeddings."""
        mock_results = [
            {
                'id': 'id1',
                'vector': [0.1, 0.2],
                'payload': {
                    'content_id': 'content1',
                    'model_name': 'test_model'
                }
            },
            {
                'id': 'id2',
                'vector': [0.3, 0.4],
                'payload': {
                    'content_id': 'content2',
                    'model_name': 'test_model'
                }
            }
        ]

        with patch.object(self.store.qdrant_client, 'retrieve_vectors') as mock_retrieve:
            mock_retrieve.return_value = mock_results

            results = self.store.retrieve_embeddings(['id1', 'id2'])
            assert len(results) == 2
            assert all(isinstance(emb, EmbeddingVector) for emb in results)

    def test_search_similar(self):
        """Test searching for similar embeddings."""
        query_embedding = EmbeddingVector.create(
            id='query_id',
            vector=[0.1, 0.2, 0.3],
            content_id='content_id',
            model_name='test_model'
        )

        mock_search_result = [
            {
                'id': 'similar_id',
                'vector': [0.15, 0.25, 0.35],
                'payload': {
                    'content_id': 'similar_content',
                    'model_name': 'test_model'
                },
                'score': 0.9
            }
        ]

        with patch.object(self.store.qdrant_client, 'search_vectors') as mock_search:
            mock_search.return_value = mock_search_result

            results = self.store.search_similar(query_embedding)
            assert len(results) == 1
            assert 'embedding' in results[0]
            assert 'score' in results[0]
            assert results[0]['score'] == 0.9

    def test_store_vector_record(self):
        """Test storing a VectorRecord."""
        record = VectorRecord.create(
            id='record_id',
            payload={'test': 'data'},
            vector=[0.1, 0.2, 0.3],
            collection_name='test_collection'
        )

        with patch.object(self.store.qdrant_client, 'store_vector') as mock_store:
            mock_store.return_value = True

            result = self.store.store_vector_record(record)
            assert result is True

    def test_store_vector_records(self):
        """Test storing multiple VectorRecords."""
        records = [
            VectorRecord.create(
                id='record1',
                payload={'test': 'data1'},
                vector=[0.1, 0.2],
                collection_name='test_collection'
            ),
            VectorRecord.create(
                id='record2',
                payload={'test': 'data2'},
                vector=[0.3, 0.4],
                collection_name='test_collection'
            )
        ]

        with patch.object(self.store.qdrant_client, 'store_vectors') as mock_store:
            mock_store.return_value = True

            result = self.store.store_vector_records(records)
            assert result is True


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__])