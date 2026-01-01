"""Module for verifying vector storage and queryability."""

from typing import List, Dict, Any
from src.storage.vector_store import VectorStore
from src.models.embedding_vector import EmbeddingVector
from src.models.book_content import BookContent
from src.utils.logger import app_logger
from src.exceptions import VectorStorageError
import time


class VerificationService:
    """Class to handle verification of vector storage and queryability."""

    def __init__(self, vector_store: VectorStore):
        """
        Initialize the verification service.

        Args:
            vector_store: VectorStore instance to verify
        """
        self.vector_store = vector_store

    def verify_storage_by_id(
        self,
        embedding_ids: List[str],
        expected_count: int = None
    ) -> Dict[str, Any]:
        """
        Verify that embeddings are properly stored by retrieving them by ID.

        Args:
            embedding_ids: List of embedding IDs to verify
            expected_count: Expected number of embeddings to retrieve

        Returns:
            Dictionary with verification results
        """
        try:
            app_logger.info(f"Verifying storage for {len(embedding_ids)} embeddings")

            # Retrieve embeddings by ID
            retrieved_embeddings = self.vector_store.retrieve_embeddings(embedding_ids)
            retrieved_ids = [emb.id for emb in retrieved_embeddings]

            # Calculate verification metrics
            successfully_retrieved = len(retrieved_ids)
            requested_count = len(embedding_ids)
            missing_ids = [eid for eid in embedding_ids if eid not in retrieved_ids]

            verification_result = {
                'total_requested': requested_count,
                'successfully_retrieved': successfully_retrieved,
                'missing_ids': missing_ids,
                'success_rate': successfully_retrieved / requested_count if requested_count > 0 else 0,
                'verification_passed': len(missing_ids) == 0,
                'expected_count': expected_count,
                'expected_match': expected_count is None or expected_count == successfully_retrieved
            }

            app_logger.info(f"Storage verification completed: {verification_result}")
            return verification_result

        except Exception as e:
            app_logger.error(f"Error during storage verification: {str(e)}")
            raise VectorStorageError(f"Storage verification failed: {str(e)}")

    def verify_similarity_search(
        self,
        query_embedding: EmbeddingVector,
        expected_min_score: float = 0.5,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Verify that similarity search works properly.

        Args:
            query_embedding: Embedding to use for similarity search
            expected_min_score: Minimum expected similarity score
            limit: Maximum number of results to return

        Returns:
            Dictionary with search verification results
        """
        try:
            app_logger.info(f"Verifying similarity search with query embedding ID: {query_embedding.id}")

            # Perform similarity search
            search_results = self.vector_store.search_similar(query_embedding, limit=limit)

            # Analyze results
            high_score_results = [r for r in search_results if r['score'] >= expected_min_score]
            avg_score = sum(r['score'] for r in search_results) / len(search_results) if search_results else 0

            search_verification = {
                'total_results': len(search_results),
                'high_score_results': len(high_score_results),
                'average_score': avg_score,
                'expected_min_score': expected_min_score,
                'search_functional': len(search_results) > 0,
                'quality_score': avg_score >= expected_min_score,
                'results': [
                    {
                        'id': r['embedding'].id,
                        'score': r['score'],
                        'model': r['embedding'].model_name
                    } for r in search_results
                ]
            }

            app_logger.info(f"Search verification completed: {search_verification}")
            return search_verification

        except Exception as e:
            app_logger.error(f"Error during search verification: {str(e)}")
            raise VectorStorageError(f"Search verification failed: {str(e)}")

    def run_performance_test(
        self,
        test_embeddings: List[EmbeddingVector],
        search_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Run performance tests on the vector storage.

        Args:
            test_embeddings: List of embeddings to test with
            search_iterations: Number of search iterations to perform

        Returns:
            Dictionary with performance metrics
        """
        try:
            app_logger.info(f"Running performance tests with {len(test_embeddings)} embeddings")

            if not test_embeddings:
                return {'error': 'No test embeddings provided'}

            # Test storage performance
            start_time = time.time()
            store_success = self.vector_store.store_embeddings(test_embeddings)
            storage_time = time.time() - start_time

            # Test retrieval performance
            embedding_ids = [emb.id for emb in test_embeddings]
            start_time = time.time()
            retrieved_embeddings = self.vector_store.retrieve_embeddings(embedding_ids)
            retrieval_time = time.time() - start_time

            # Test search performance
            if test_embeddings:
                search_times = []
                for _ in range(search_iterations):
                    start_time = time.time()
                    self.vector_store.search_similar(test_embeddings[0], limit=5)
                    search_time = time.time() - start_time
                    search_times.append(search_time)

                avg_search_time = sum(search_times) / len(search_times)
                min_search_time = min(search_times)
                max_search_time = max(search_times)
            else:
                avg_search_time = min_search_time = max_search_time = 0

            performance_metrics = {
                'storage_time_seconds': storage_time,
                'retrieval_time_seconds': retrieval_time,
                'avg_search_time_seconds': avg_search_time,
                'min_search_time_seconds': min_search_time,
                'max_search_time_seconds': max_search_time,
                'search_iterations': search_iterations,
                'embedding_count': len(test_embeddings),
                'storage_success': store_success,
                'retrieval_count': len(retrieved_embeddings),
                'performance_acceptable': avg_search_time < 2.0  # Less than 2 seconds per search
            }

            app_logger.info(f"Performance test completed: {performance_metrics}")
            return performance_metrics

        except Exception as e:
            app_logger.error(f"Error during performance testing: {str(e)}")
            raise VectorStorageError(f"Performance testing failed: {str(e)}")

    def run_comprehensive_verification(
        self,
        test_embeddings: List[EmbeddingVector],
        test_contents: List[BookContent] = None,
        expected_min_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Run comprehensive verification of the entire pipeline.

        Args:
            test_embeddings: List of test embeddings to verify
            test_contents: Optional list of test contents
            expected_min_score: Minimum expected similarity score

        Returns:
            Dictionary with comprehensive verification results
        """
        try:
            app_logger.info(f"Starting comprehensive verification for {len(test_embeddings)} embeddings")

            if not test_embeddings:
                return {'error': 'No test embeddings provided'}

            # Store test embeddings
            app_logger.info("Storing test embeddings...")
            store_success = self.vector_store.store_embeddings(test_embeddings, test_contents)

            if not store_success:
                return {'error': 'Failed to store test embeddings'}

            # Get embedding IDs for verification
            embedding_ids = [emb.id for emb in test_embeddings]

            # Verify storage
            app_logger.info("Verifying storage...")
            storage_verification = self.verify_storage_by_id(embedding_ids)

            # Verify search functionality with the first embedding
            app_logger.info("Verifying search functionality...")
            search_verification = self.verify_similarity_search(
                test_embeddings[0],
                expected_min_score=expected_min_score
            )

            # Run performance tests
            app_logger.info("Running performance tests...")
            performance_metrics = self.run_performance_test(test_embeddings)

            # Compile comprehensive results
            comprehensive_results = {
                'storage_verification': storage_verification,
                'search_verification': search_verification,
                'performance_metrics': performance_metrics,
                'overall_success': (
                    storage_verification.get('verification_passed', False) and
                    search_verification.get('search_functional', False) and
                    performance_metrics.get('performance_acceptable', False)
                ),
                'verification_completed': True,
                'timestamp': time.time()
            }

            app_logger.info(f"Comprehensive verification completed: Overall success = {comprehensive_results['overall_success']}")
            return comprehensive_results

        except Exception as e:
            app_logger.error(f"Error during comprehensive verification: {str(e)}")
            raise VectorStorageError(f"Comprehensive verification failed: {str(e)}")


    def run_comprehensive_verification(
        self,
        test_embeddings: List[EmbeddingVector],
        test_contents: List[BookContent] = None,
        expected_min_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        Run comprehensive verification of the entire pipeline.

        Args:
            test_embeddings: List of test embeddings to verify
            test_contents: Optional list of test contents
            expected_min_score: Minimum expected similarity score

        Returns:
            Dictionary with comprehensive verification results
        """
        try:
            app_logger.info(f"Starting comprehensive verification for {len(test_embeddings)} embeddings")

            if not test_embeddings:
                return {'error': 'No test embeddings provided'}

            # Store test embeddings
            app_logger.info("Storing test embeddings...")
            store_success = self.vector_store.store_embeddings(test_embeddings, test_contents)

            if not store_success:
                return {'error': 'Failed to store test embeddings'}

            # Get embedding IDs for verification
            embedding_ids = [emb.id for emb in test_embeddings]

            # Verify storage
            app_logger.info("Verifying storage...")
            storage_verification = self.verify_storage_by_id(embedding_ids)

            # Verify search functionality with the first embedding
            app_logger.info("Verifying search functionality...")
            search_verification = self.verify_similarity_search(
                test_embeddings[0],
                expected_min_score=expected_min_score
            )

            # Run performance tests
            app_logger.info("Running performance tests...")
            performance_metrics = self.run_performance_test(test_embeddings)

            # Compile comprehensive results
            comprehensive_results = {
                'storage_verification': storage_verification,
                'search_verification': search_verification,
                'performance_metrics': performance_metrics,
                'overall_success': (
                    storage_verification.get('verification_passed', False) and
                    search_verification.get('search_functional', False) and
                    performance_metrics.get('performance_acceptable', False)
                ),
                'verification_completed': True,
                'timestamp': time.time()
            }

            app_logger.info(f"Comprehensive verification completed: Overall success = {comprehensive_results['overall_success']}")
            return comprehensive_results

        except Exception as e:
            app_logger.error(f"Error during comprehensive verification: {str(e)}")
            raise VectorStorageError(f"Comprehensive verification failed: {str(e)}")


# For command-line usage
def main():
    """Command-line interface for verification."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Verification of vector storage and queryability')
    parser.add_argument('--action', type=str, choices=['verify-storage', 'verify-search', 'comprehensive'],
                       default='comprehensive', help='Verification action to perform')

    args = parser.parse_args()

    try:
        # This would require actual Qdrant setup to run properly
        print(f"Performing {args.action} verification...")
        print("Note: This requires a configured Qdrant instance to run properly.")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()