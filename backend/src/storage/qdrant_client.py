"""Module for interacting with Qdrant Cloud for vector storage."""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from src.config import Config
from src.exceptions import VectorStorageError, ConfigurationError, QdrantConnectionError
from src.utils.logger import app_logger


class QdrantClientWrapper:
    """Class to handle interactions with Qdrant Cloud."""

    def __init__(
        self,
        api_key: str = None,
        host: str = None,
        port: int = None,
        collection_name: str = None
    ):
        """
        Initialize the Qdrant client wrapper.

        Args:
            api_key: Qdrant API key (defaults to config)
            host: Qdrant host (defaults to config)
            port: Qdrant port (defaults to config)
            collection_name: Name of the collection (defaults to config)
        """
        self.api_key = api_key or Config.QDRANT_API_KEY
        self.host = host or Config.QDRANT_HOST
        self.port = port or Config.QDRANT_PORT
        self.collection_name = collection_name or Config.QDRANT_COLLECTION_NAME

        if not self.api_key or not self.host:
            raise ConfigurationError("Qdrant API key and host are required")

        try:
            # Initialize the Qdrant client - for cloud use URL parameter
            if self.host.startswith(('http://', 'https://')):
                self.client = QdrantClient(
                    url=self.host,
                    api_key=self.api_key,
                    prefer_grpc=True
                )
            else:
                # For local instance
                self.client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    api_key=self.api_key
                )
        except Exception as e:
            app_logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            raise QdrantConnectionError(f"Failed to initialize Qdrant client: {str(e)}")

    def create_collection(
        self,
        vector_size: int = 1024,  # Default size, will be updated based on actual embeddings
        distance: str = "Cosine"
    ) -> bool:
        """
        Create a collection in Qdrant if it doesn't exist.

        Args:
            vector_size: Size of the vectors
            distance: Distance metric to use

        Returns:
            True if collection was created or already exists
        """
        try:
            # Convert distance string to Distance enum
            distance_enum = Distance.COSINE if distance.lower() == "cosine" else Distance.EUCLID
            if distance.lower() == "dot":
                distance_enum = Distance.DOT

            # Check if collection already exists
            collections = self.client.get_collections()
            existing_collection = None
            for collection in collections.collections:
                if collection.name == self.collection_name:
                    existing_collection = collection
                    break

            if existing_collection:
                app_logger.info(f"Collection {self.collection_name} already exists")
                return True

            # Create the collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_enum
                )
            )

            app_logger.info(f"Created collection {self.collection_name}")
            return True

        except Exception as e:
            app_logger.error(f"Error creating collection {self.collection_name}: {str(e)}")
            raise VectorStorageError(f"Failed to create collection {self.collection_name}: {str(e)}")

    def store_vector(
        self,
        vector_id: str,
        vector: List[float],
        payload: Dict[str, Any]
    ) -> bool:
        """
        Store a single vector in Qdrant.

        Args:
            vector_id: Unique ID for the vector
            vector: The vector to store
            payload: Metadata to store with the vector

        Returns:
            True if successful
        """
        try:
            # Ensure collection exists
            self.create_collection(vector_size=len(vector))

            # Store the vector
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=vector_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )

            app_logger.info(f"Stored vector with ID {vector_id} in collection {self.collection_name}")
            return True

        except Exception as e:
            app_logger.error(f"Error storing vector {vector_id}: {str(e)}")
            raise VectorStorageError(f"Failed to store vector {vector_id}: {str(e)}")

    def store_vectors(
        self,
        vector_ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> bool:
        """
        Store multiple vectors in Qdrant.

        Args:
            vector_ids: List of unique IDs for the vectors
            vectors: List of vectors to store
            payloads: List of metadata to store with the vectors

        Returns:
            True if successful
        """
        if not vector_ids or not vectors or not payloads:
            app_logger.warning("Empty vectors list provided to store_vectors")
            return True

        if len(vector_ids) != len(vectors) or len(vectors) != len(payloads):
            raise VectorStorageError("Vector IDs, vectors, and payloads must have the same length")

        try:
            # Ensure collection exists - use the size of the first vector
            if vectors:
                self.create_collection(vector_size=len(vectors[0]))

            # Prepare points for batch storage
            points = []
            for vector_id, vector, payload in zip(vector_ids, vectors, payloads):
                points.append(
                    models.PointStruct(
                        id=vector_id,
                        vector=vector,
                        payload=payload
                    )
                )

            # Store vectors in batch
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            app_logger.info(f"Stored {len(vector_ids)} vectors in collection {self.collection_name}")
            return True

        except Exception as e:
            app_logger.error(f"Error storing batch of vectors: {str(e)}")
            raise VectorStorageError(f"Failed to store batch of vectors: {str(e)}")

    def retrieve_vector(
        self,
        vector_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single vector by ID from Qdrant.

        Args:
            vector_id: ID of the vector to retrieve

        Returns:
            Dictionary with vector and payload, or None if not found
        """
        try:
            # Retrieve the point
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[vector_id],
                with_payload=True,
                with_vectors=True
            )

            if points and len(points) > 0:
                point = points[0]
                return {
                    'id': point.id,
                    'vector': point.vector,
                    'payload': point.payload
                }

            app_logger.info(f"Vector with ID {vector_id} not found")
            return None

        except Exception as e:
            app_logger.error(f"Error retrieving vector {vector_id}: {str(e)}")
            raise VectorStorageError(f"Failed to retrieve vector {vector_id}: {str(e)}")

    def retrieve_vectors(
        self,
        vector_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Retrieve multiple vectors by IDs from Qdrant.

        Args:
            vector_ids: List of IDs of the vectors to retrieve

        Returns:
            List of dictionaries with vector and payload
        """
        if not vector_ids:
            return []

        try:
            # Retrieve the points
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=vector_ids,
                with_payload=True,
                with_vectors=True
            )

            results = []
            for point in points:
                results.append({
                    'id': point.id,
                    'vector': point.vector,
                    'payload': point.payload
                })

            app_logger.info(f"Retrieved {len(results)} vectors out of {len(vector_ids)} requested")
            return results

        except Exception as e:
            app_logger.error(f"Error retrieving vectors: {str(e)}")
            raise VectorStorageError(f"Failed to retrieve vectors: {str(e)}")

    def search_vectors(
        self,
        query_vector: List[float],
        limit: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using similarity search.

        Args:
            query_vector: The vector to search for similar ones to
            limit: Maximum number of results to return
            filter_dict: Optional filter for the search

        Returns:
            List of similar vectors with scores
        """
        try:
            # Convert filter to Qdrant format if provided
            search_filter = None
            if filter_dict:
                conditions = []
                for key, value in filter_dict.items():
                    conditions.append(models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    ))
                if conditions:
                    search_filter = models.Filter(must=conditions)

            # Perform the search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter,
                with_payload=True,
                with_vectors=True
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'vector': result.vector,
                    'payload': result.payload,
                    'score': result.score
                })

            app_logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            app_logger.error(f"Error searching vectors: {str(e)}")
            raise VectorStorageError(f"Failed to search vectors: {str(e)}")

    def delete_vectors(
        self,
        vector_ids: List[str]
    ) -> bool:
        """
        Delete vectors by IDs from Qdrant.

        Args:
            vector_ids: List of IDs of vectors to delete

        Returns:
            True if successful
        """
        if not vector_ids:
            return True

        try:
            # Delete the points
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=vector_ids
                )
            )

            app_logger.info(f"Deleted {len(vector_ids)} vectors from collection {self.collection_name}")
            return True

        except Exception as e:
            app_logger.error(f"Error deleting vectors: {str(e)}")
            raise VectorStorageError(f"Failed to delete vectors: {str(e)}")

    def validate_connection(self) -> bool:
        """
        Validate that the Qdrant connection is working.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to get collection info as a basic connection test
            collections = self.client.get_collections()
            app_logger.info(f"Successfully connected to Qdrant, found {len(collections.collections)} collections")
            return True
        except Exception as e:
            app_logger.error(f"Qdrant connection validation failed: {str(e)}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'name': collection_info.config.params.vectors.size,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance,
                'point_count': collection_info.count
            }
        except Exception as e:
            app_logger.error(f"Error getting collection info: {str(e)}")
            raise VectorStorageError(f"Failed to get collection info: {str(e)}")


# For command-line usage
def main():
    """Command-line interface for testing Qdrant client."""
    import argparse

    parser = argparse.ArgumentParser(description='Test Qdrant vector storage')
    parser.add_argument('--vector', type=str, required=True, help='Vector as comma-separated values (e.g., "0.1,0.2,0.3")')
    parser.add_argument('--id', type=str, required=True, help='Vector ID')
    parser.add_argument('--action', type=str, choices=['store', 'retrieve'], default='store', help='Action to perform')

    args = parser.parse_args()

    try:
        client = QdrantClientWrapper()

        vector = [float(x) for x in args.vector.split(',')]

        if args.action == 'store':
            success = client.store_vector(args.id, vector, {"test": True})
            print(f"Vector stored successfully: {success}")
        elif args.action == 'retrieve':
            result = client.retrieve_vector(args.id)
            if result:
                print(f"Retrieved vector ID: {result['id']}")
                print(f"Vector length: {len(result['vector'])}")
                print(f"Payload: {result['payload']}")
            else:
                print("Vector not found")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()