"""Tests for main pipeline integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from main import run_pipeline
from src.models.book_content import BookContent
from src.models.embedding_vector import EmbeddingVector


class TestMainPipeline:
    """Test cases for the main pipeline integration."""

    def test_run_pipeline_success(self):
        """Test successful execution of the full pipeline."""
        urls = ['https://example.com']

        with patch('src.config.Config.validate') as mock_config_validate:
            mock_config_validate.return_value = True

            with patch('src.ingestion.pipeline.ContentExtractionPipeline.run') as mock_extraction_run:
                mock_content = BookContent.create(
                    id='test_id',
                    url='https://example.com',
                    title='Test Title',
                    content='Test content',
                    metadata={}
                )
                mock_extraction_run.return_value = {
                    'contents': [mock_content],
                    'stats': {'total_urls_processed': 1, 'total_content_chunks': 1}
                }

                with patch('src.embeddings.generator.EmbeddingGenerator.run') as mock_embedding_run:
                    mock_embedding = EmbeddingVector.create(
                        id='embedding_id',
                        vector=[0.1, 0.2, 0.3],
                        content_id='test_id',
                        model_name='test_model'
                    )
                    mock_embedding_run.return_value = [mock_embedding]

                    with patch('src.storage.vector_store.VectorStore.run') as mock_storage_run:
                        mock_storage_run.return_value = True

                        result = run_pipeline(urls)

                        assert result['success'] is True
                        assert result['extraction_stats']['total_urls_processed'] == 1
                        assert result['embedding_count'] == 1
                        assert result['storage_success'] is True

    def test_run_pipeline_no_content(self):
        """Test pipeline when no content is extracted."""
        urls = ['https://example.com']

        with patch('src.config.Config.validate') as mock_config_validate:
            mock_config_validate.return_value = True

            with patch('src.ingestion.pipeline.ContentExtractionPipeline.run') as mock_extraction_run:
                mock_extraction_run.return_value = {
                    'contents': [],
                    'stats': {'total_urls_processed': 1, 'total_content_chunks': 0}
                }

                result = run_pipeline(urls)
                assert result['success'] is False
                assert 'No content extracted' in result['error']

    def test_run_pipeline_no_embeddings(self):
        """Test pipeline when no embeddings are generated."""
        urls = ['https://example.com']

        with patch('src.config.Config.validate') as mock_config_validate:
            mock_config_validate.return_value = True

            with patch('src.ingestion.pipeline.ContentExtractionPipeline.run') as mock_extraction_run:
                mock_content = BookContent.create(
                    id='test_id',
                    url='https://example.com',
                    title='Test Title',
                    content='Test content',
                    metadata={}
                )
                mock_extraction_run.return_value = {
                    'contents': [mock_content],
                    'stats': {'total_urls_processed': 1, 'total_content_chunks': 1}
                }

                with patch('src.embeddings.generator.EmbeddingGenerator.run') as mock_embedding_run:
                    mock_embedding_run.return_value = []  # No embeddings generated

                    result = run_pipeline(urls)
                    assert result['success'] is False
                    assert 'No embeddings generated' in result['error']

    def test_run_pipeline_storage_failure(self):
        """Test pipeline when storage fails."""
        urls = ['https://example.com']

        with patch('src.config.Config.validate') as mock_config_validate:
            mock_config_validate.return_value = True

            with patch('src.ingestion.pipeline.ContentExtractionPipeline.run') as mock_extraction_run:
                mock_content = BookContent.create(
                    id='test_id',
                    url='https://example.com',
                    title='Test Title',
                    content='Test content',
                    metadata={}
                )
                mock_extraction_run.return_value = {
                    'contents': [mock_content],
                    'stats': {'total_urls_processed': 1, 'total_content_chunks': 1}
                }

                with patch('src.embeddings.generator.EmbeddingGenerator.run') as mock_embedding_run:
                    mock_embedding = EmbeddingVector.create(
                        id='embedding_id',
                        vector=[0.1, 0.2, 0.3],
                        content_id='test_id',
                        model_name='test_model'
                    )
                    mock_embedding_run.return_value = [mock_embedding]

                    with patch('src.storage.vector_store.VectorStore.run') as mock_storage_run:
                        mock_storage_run.return_value = False  # Storage failed

                        result = run_pipeline(urls)
                        assert result['success'] is False
                        assert 'Vector storage failed' in result['error']

    def test_run_pipeline_with_verification(self):
        """Test pipeline with verification enabled."""
        urls = ['https://example.com']
        config = {'verify': True}

        with patch('src.config.Config.validate') as mock_config_validate:
            mock_config_validate.return_value = True

            with patch('src.ingestion.pipeline.ContentExtractionPipeline.run') as mock_extraction_run:
                mock_content = BookContent.create(
                    id='test_id',
                    url='https://example.com',
                    title='Test Title',
                    content='Test content',
                    metadata={}
                )
                mock_extraction_run.return_value = {
                    'contents': [mock_content],
                    'stats': {'total_urls_processed': 1, 'total_content_chunks': 1}
                }

                with patch('src.embeddings.generator.EmbeddingGenerator.run') as mock_embedding_run:
                    mock_embedding = EmbeddingVector.create(
                        id='embedding_id',
                        vector=[0.1, 0.2, 0.3],
                        content_id='test_id',
                        model_name='test_model'
                    )
                    mock_embedding_run.return_value = [mock_embedding]

                    with patch('src.storage.vector_store.VectorStore.run') as mock_storage_run:
                        mock_storage_run.return_value = True

                        with patch('src.storage.verification.VerificationService.run_comprehensive_verification') as mock_verification:
                            mock_verification.return_value = {
                                'overall_success': True,
                                'verification_completed': True
                            }

                            result = run_pipeline(urls, config)

                            assert result['success'] is True
                            assert result['verification_result'] is not None
                            mock_verification.assert_called_once()


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__])