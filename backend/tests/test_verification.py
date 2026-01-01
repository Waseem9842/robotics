"""Tests for verification functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.storage.verification import VerificationService
from src.storage.vector_store import VectorStore
from src.models.embedding_vector import EmbeddingVector
from src.models.book_content import BookContent


class TestVerificationService:
    """Test cases for VerificationService class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        with patch('qdrant_client.QdrantClient'):
            vector_store = VectorStore(
                api_key='test_key',
                host='https://test.qdrant.io',
                collection_name='test_collection'
            )
            self.verification_service = VerificationService(vector_store)

    def test_verify_storage_by_id(self):
        """Test storage verification by ID."""
        embedding_ids = ['id1', 'id2', 'id3']

        with patch.object(self.verification_service.vector_store, 'retrieve_embeddings') as mock_retrieve:
            mock_retrieve.return_value = [
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

            result = self.verification_service.verify_storage_by_id(embedding_ids)
            assert result['total_requested'] == 3
            assert result['successfully_retrieved'] == 2
            assert 'id3' in result['missing_ids']
            assert result['success_rate'] == 2/3
            assert result['verification_passed'] is False

    def test_verify_similarity_search(self):
        """Test similarity search verification."""
        query_embedding = EmbeddingVector.create(
            id='query_id',
            vector=[0.1, 0.2, 0.3],
            content_id='content_id',
            model_name='test_model'
        )

        mock_search_result = [
            {
                'embedding': EmbeddingVector.create(
                    id='similar_id',
                    vector=[0.15, 0.25, 0.35],
                    content_id='similar_content',
                    model_name='test_model'
                ),
                'score': 0.85,
                'payload': {}
            }
        ]

        with patch.object(self.verification_service.vector_store, 'search_similar') as mock_search:
            mock_search.return_value = mock_search_result

            result = self.verification_service.verify_similarity_search(query_embedding)
            assert result['total_results'] == 1
            assert result['high_score_results'] == 1  # With default min score of 0.5
            assert result['average_score'] == 0.85
            assert result['search_functional'] is True

    def test_run_performance_test(self):
        """Test performance testing."""
        test_embeddings = [
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

        with patch.object(self.verification_service.vector_store, 'store_embeddings') as mock_store:
            mock_store.return_value = True

            with patch.object(self.verification_service.vector_store, 'retrieve_embeddings') as mock_retrieve:
                mock_retrieve.return_value = test_embeddings

                with patch.object(self.verification_service.vector_store, 'search_similar') as mock_search:
                    mock_search.return_value = [
                        {
                            'embedding': test_embeddings[0],
                            'score': 0.9,
                            'payload': {}
                        }
                    ]

                    result = self.verification_service.run_performance_test(test_embeddings, search_iterations=2)
                    assert 'storage_time_seconds' in result
                    assert 'retrieval_time_seconds' in result
                    assert 'avg_search_time_seconds' in result
                    assert result['embedding_count'] == 2

    def test_run_comprehensive_verification(self):
        """Test comprehensive verification."""
        test_embeddings = [
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

        test_contents = [
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

        with patch.object(self.verification_service, 'verify_storage_by_id') as mock_verify_storage:
            mock_verify_storage.return_value = {
                'total_requested': 2,
                'successfully_retrieved': 2,
                'verification_passed': True
            }

            with patch.object(self.verification_service, 'verify_similarity_search') as mock_verify_search:
                mock_verify_search.return_value = {
                    'total_results': 1,
                    'search_functional': True
                }

                with patch.object(self.verification_service, 'run_performance_test') as mock_perf_test:
                    mock_perf_test.return_value = {
                        'performance_acceptable': True
                    }

                    result = self.verification_service.run_comprehensive_verification(
                        test_embeddings, test_contents
                    )
                    assert result['verification_completed'] is True
                    assert result['overall_success'] is True
                    assert 'storage_verification' in result
                    assert 'search_verification' in result
                    assert 'performance_metrics' in result


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__])