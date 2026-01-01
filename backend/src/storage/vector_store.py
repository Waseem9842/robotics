"""Module for vector storage and retrieval operations."""

from typing import List, Dict, Any, Optional
from src.storage.qdrant_client import QdrantClientWrapper
from src.models.embedding_vector import EmbeddingVector
from src.models.vector_record import VectorRecord
from src.models.book_content import BookContent
from src.utils.logger import app_logger
from src.exceptions import VectorStorageError
from src.config import Config


class VectorStore:
    """Class to handle vector storage and retrieval operations."""

    def __init__(
        self,
        api_key: str = None,
        host: str = None,
        port: int = None,
        collection_name: str = None
    ):
        """
        Initialize the vector store.

        Args:
            api_key: Qdrant API key (defaults to config)
            host: Qdrant host (defaults to config)
            port: Qdrant port (defaults to config)
            collection_name: Name of the collection (defaults to config)
        """
        self.qdrant_client = QdrantClientWrapper(
            api_key=api_key,
            host=host,
            port=port,
            collection_name=collection_name
        )

    def store_embedding(self, embedding: EmbeddingVector, content: BookContent = None) -> bool:
        """
        Store a single embedding vector with associated content metadata.

        Args:
            embedding: EmbeddingVector to store
            content: Optional BookContent to include in payload

        Returns:
            True if successful
        """
        try:
            # Prepare payload with embedding and content metadata
            payload = {
                'content_id': embedding.content_id,
                'model_name': embedding.model_name,
                'created_at': embedding.created_at.isoformat()
            }

            # Include content metadata if provided
            if content:
                payload.update({
                    'content_url': content.url,
                    'content_title': content.title,
                    'content_metadata': content.metadata
                })

            # Store the vector
            success = self.qdrant_client.store_vector(
                vector_id=embedding.id,
                vector=embedding.vector,
                payload=payload
            )

            app_logger.info(f"Stored embedding vector with ID: {embedding.id}")
            return success

        except Exception as e:
            app_logger.error(f"Error storing embedding {embedding.id}: {str(e)}")
            raise VectorStorageError(f"Failed to store embedding {embedding.id}: {str(e)}")

    def store_embeddings(self, embeddings: List[EmbeddingVector], contents: List[BookContent] = None) -> bool:
        """
        Store multiple embedding vectors with associated content metadata.

        Args:
            embeddings: List of EmbeddingVector to store
            contents: Optional list of BookContent to include in payloads

        Returns:
            True if successful
        """
        if not embeddings:
            return True

        try:
            # Prepare vectors, IDs, and payloads for batch storage
            vector_ids = []
            vectors = []
            payloads = []

            for i, embedding in enumerate(embeddings):
                # Prepare payload
                payload = {
                    'content_id': embedding.content_id,
                    'model_name': embedding.model_name,
                    'created_at': embedding.created_at.isoformat()
                }

                # Include content metadata if provided
                if contents and i < len(contents):
                    content = contents[i]
                    payload.update({
                        'content_url': content.url,
                        'content_title': content.title,
                        'content_metadata': content.metadata
                    })

                vector_ids.append(embedding.id)
                vectors.append(embedding.vector)
                payloads.append(payload)

            # Store vectors in batch
            success = self.qdrant_client.store_vectors(
                vector_ids=vector_ids,
                vectors=vectors,
                payloads=payloads
            )

            app_logger.info(f"Stored {len(embeddings)} embedding vectors in batch")
            return success

        except Exception as e:
            app_logger.error(f"Error storing batch of embeddings: {str(e)}")
            raise VectorStorageError(f"Failed to store batch of embeddings: {str(e)}")

    def retrieve_embedding(self, embedding_id: str) -> Optional[EmbeddingVector]:
        """
        Retrieve a single embedding vector by ID.

        Args:
            embedding_id: ID of the embedding to retrieve

        Returns:
            EmbeddingVector if found, None otherwise
        """
        try:
            result = self.qdrant_client.retrieve_vector(embedding_id)

            if result:
                # Create EmbeddingVector from retrieved data
                return EmbeddingVector.create(
                    id=result['id'],
                    vector=result['vector'],
                    content_id=result['payload'].get('content_id', ''),
                    model_name=result['payload'].get('model_name', '')
                )

            app_logger.info(f"Embedding with ID {embedding_id} not found")
            return None

        except Exception as e:
            app_logger.error(f"Error retrieving embedding {embedding_id}: {str(e)}")
            raise VectorStorageError(f"Failed to retrieve embedding {embedding_id}: {str(e)}")

    def retrieve_embeddings(self, embedding_ids: List[str]) -> List[EmbeddingVector]:
        """
        Retrieve multiple embedding vectors by IDs.

        Args:
            embedding_ids: List of IDs of embeddings to retrieve

        Returns:
            List of EmbeddingVector instances
        """
        if not embedding_ids:
            return []

        try:
            results = self.qdrant_client.retrieve_vectors(embedding_ids)

            embeddings = []
            for result in results:
                embedding = EmbeddingVector.create(
                    id=result['id'],
                    vector=result['vector'],
                    content_id=result['payload'].get('content_id', ''),
                    model_name=result['payload'].get('model_name', '')
                )
                embeddings.append(embedding)

            app_logger.info(f"Retrieved {len(embeddings)} embeddings out of {len(embedding_ids)} requested")
            return embeddings

        except Exception as e:
            app_logger.error(f"Error retrieving embeddings: {str(e)}")
            raise VectorStorageError(f"Failed to retrieve embeddings: {str(e)}")

    def search_similar(
        self,
        query_embedding: EmbeddingVector,
        limit: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using similarity search.

        Args:
            query_embedding: EmbeddingVector to search for similar ones to
            limit: Maximum number of results to return
            filter_dict: Optional filter for the search

        Returns:
            List of dictionaries with similar embeddings and scores
        """
        try:
            results = self.qdrant_client.search_vectors(
                query_vector=query_embedding.vector,
                limit=limit,
                filter_dict=filter_dict
            )

            formatted_results = []
            for result in results:
                formatted_results.append({
                    'embedding': EmbeddingVector.create(
                        id=result['id'],
                        vector=result['vector'],
                        content_id=result['payload'].get('content_id', ''),
                        model_name=result['payload'].get('model_name', '')
                    ),
                    'score': result['score'],
                    'payload': result['payload']
                })

            app_logger.info(f"Similarity search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            app_logger.error(f"Error performing similarity search: {str(e)}")
            raise VectorStorageError(f"Failed to perform similarity search: {str(e)}")

    def store_vector_record(self, record: VectorRecord) -> bool:
        """
        Store a VectorRecord in the vector database.

        Args:
            record: VectorRecord to store

        Returns:
            True if successful
        """
        try:
            success = self.qdrant_client.store_vector(
                vector_id=record.id,
                vector=record.vector,
                payload=record.payload
            )

            app_logger.info(f"Stored vector record with ID: {record.id}")
            return success

        except Exception as e:
            app_logger.error(f"Error storing vector record {record.id}: {str(e)}")
            raise VectorStorageError(f"Failed to store vector record {record.id}: {str(e)}")

    def store_vector_records(self, records: List[VectorRecord]) -> bool:
        """
        Store multiple VectorRecords in the vector database.

        Args:
            records: List of VectorRecord to store

        Returns:
            True if successful
        """
        if not records:
            return True

        try:
            # Prepare vectors, IDs, and payloads for batch storage
            vector_ids = [record.id for record in records]
            vectors = [record.vector for record in records]
            payloads = [record.payload for record in records]

            success = self.qdrant_client.store_vectors(
                vector_ids=vector_ids,
                vectors=vectors,
                payloads=payloads
            )

            app_logger.info(f"Stored {len(records)} vector records in batch")
            return success

        except Exception as e:
            app_logger.error(f"Error storing batch of vector records: {str(e)}")
            raise VectorStorageError(f"Failed to store batch of vector records: {str(e)}")

    def run(self, embeddings: List[EmbeddingVector], contents: List[BookContent] = None) -> bool:
        """
        Run the vector storage pipeline.

        Args:
            embeddings: List of EmbeddingVector to store
            contents: Optional list of BookContent to include in payloads

        Returns:
            True if successful
        """
        app_logger.info(f"Starting vector storage pipeline for {len(embeddings)} embeddings")

        try:
            success = self.store_embeddings(embeddings, contents)
            app_logger.info("Vector storage pipeline completed successfully")
            return success

        except Exception as e:
            app_logger.error(f"Vector storage pipeline failed: {str(e)}")
            raise VectorStorageError(f"Vector storage pipeline failed: {str(e)}")


    def verify_storage(self, embedding_ids: List[str]) -> Dict[str, Any]:
        """
        Verify that embeddings are properly stored by retrieving them.

        Args:
            embedding_ids: List of embedding IDs to verify

        Returns:
            Dictionary with verification results
        """
        try:
            retrieved_embeddings = self.retrieve_embeddings(embedding_ids)
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
                'verification_passed': len(missing_ids) == 0
            }

            app_logger.info(f"Storage verification completed: {verification_result}")
            return verification_result

        except Exception as e:
            app_logger.error(f"Error during storage verification: {str(e)}")
            raise VectorStorageError(f"Storage verification failed: {str(e)}")

    def run_end_to_end_verification(
        self,
        test_embeddings: List[EmbeddingVector],
        test_contents: List[BookContent] = None
    ) -> Dict[str, Any]:
        """
        Run end-to-end verification of the pipeline.

        Args:
            test_embeddings: List of test embeddings to store and verify
            test_contents: Optional list of test contents to include in storage

        Returns:
            Dictionary with verification results
        """
        if not test_embeddings:
            return {'error': 'No test embeddings provided'}

        try:
            app_logger.info(f"Starting end-to-end verification for {len(test_embeddings)} embeddings")

            # Store the test embeddings
            store_success = self.store_embeddings(test_embeddings, test_contents)
            if not store_success:
                return {'error': 'Failed to store test embeddings'}

            # Get the IDs of embeddings to verify
            embedding_ids = [emb.id for emb in test_embeddings]

            # Verify storage
            storage_verification = self.verify_storage(embedding_ids)

            # Perform a similarity search to verify queryability
            search_results = []
            if test_embeddings:
                # Use the first embedding for similarity search
                first_embedding = test_embeddings[0]
                search_results = self.search_similar(first_embedding, limit=min(5, len(test_embeddings)))

            # Compile results
            verification_results = {
                'storage_verification': storage_verification,
                'search_results_count': len(search_results),
                'verification_completed': True,
                'overall_success': storage_verification.get('verification_passed', False)
            }

            app_logger.info(f"End-to-end verification completed: {verification_results}")
            return verification_results

        except Exception as e:
            app_logger.error(f"Error during end-to-end verification: {str(e)}")
            raise VectorStorageError(f"End-to-end verification failed: {str(e)}")


# For command-line usage
def main():
    """Command-line interface for the vector store."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Vector storage operations')
    parser.add_argument('--vector', type=str, required=True, help='Vector as comma-separated values (e.g., "0.1,0.2,0.3")')
    parser.add_argument('--id', type=str, required=True, help='Vector ID')
    parser.add_argument('--action', type=str, choices=['store', 'retrieve'], default='store', help='Action to perform')

    args = parser.parse_args()

    try:
        store = VectorStore()

        vector = [float(x) for x in args.vector.split(',')]
        embedding = EmbeddingVector.create(
            id=args.id,
            vector=vector,
            content_id="test_content",
            model_name="test_model"
        )

        if args.action == 'store':
            success = store.store_embedding(embedding)
            print(f"Embedding stored successfully: {success}")
        elif args.action == 'retrieve':
            result = store.retrieve_embedding(args.id)
            if result:
                print(f"Retrieved embedding ID: {result.id}")
                print(f"Vector length: {len(result.vector)}")
                print(f"Model: {result.model_name}")
            else:
                print("Embedding not found")
    except Exception as e:
        app_logger.error(f"Error in command-line vector storage: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()