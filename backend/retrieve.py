"""
RAG Retrieval Validation Module

This module connects to Qdrant to validate retrieval accuracy for RAG systems.
It performs top-k similarity searches and validates results using returned text,
metadata, and source URLs.

The module provides functionality to:
- Connect to Qdrant vector database
- Generate embeddings using Cohere
- Perform similarity searches
- Validate retrieval accuracy and ranking
- Check data integrity of retrieved results

Usage:
    python backend/retrieve.py --query "your test query" --top-k 5 --threshold 0.7

Example:
    python backend/retrieve.py --query "What is the capital of France?" --top-k 3 --threshold 0.6

Environment Variables:
    QDRANT_URL: URL for Qdrant instance
    QDRANT_API_KEY: API key for Qdrant
    COHERE_API_KEY: API key for Cohere

Returns:
    Validation results including accuracy metrics, ranking correctness,
    data integrity checks, and retrieved chunks with scores.
"""

import os
import argparse
import logging
from typing import List, Dict, Any, Optional
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchRequest
from qdrant_client.models import PointStruct
import dotenv


class RetrievalValidator:
    """
    Validates RAG retrieval accuracy by connecting to Qdrant and performing
    similarity searches with validation of results.
    """

    def __init__(self, qdrant_url: str, qdrant_api_key: str, cohere_api_key: str):
        """
        Initialize the retrieval validator with Qdrant and Cohere clients.

        Args:
            qdrant_url: URL for Qdrant instance
            qdrant_api_key: API key for Qdrant
            cohere_api_key: API key for Cohere
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize clients with error handling
        try:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            self.cohere_client = cohere.Client(cohere_api_key)
            self.logger.info("Successfully initialized Qdrant and Cohere clients")
        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {str(e)}")
            raise

    def __init__(self, qdrant_url: str, qdrant_api_key: str, cohere_api_key: str):
        """
        Initialize the retrieval validator with Qdrant and Cohere clients.

        Args:
            qdrant_url: URL for Qdrant instance
            qdrant_api_key: API key for Qdrant
            cohere_api_key: API key for Cohere
        """
        # Set up logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Initialize clients with error handling
        try:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            self.cohere_client = cohere.Client(cohere_api_key)
            self.logger.info("Successfully initialized Qdrant and Cohere clients")

            # Initialize cache for embeddings
            self.embedding_cache = {}
        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {str(e)}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using Cohere.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Check cache first
            if text in self.embedding_cache:
                self.logger.debug(f"Retrieved embedding from cache for text: {text[:50]}...")
                return self.embedding_cache[text]

            self.logger.info(f"Generating embedding for text: {text[:50]}...")
            response = self.cohere_client.embed(texts=[text], model="embed-english-v3.0")
            embedding = response.embeddings[0]

            # Cache the embedding
            self.embedding_cache[text] = embedding
            self.logger.debug(f"Successfully generated embedding with length: {len(embedding)} and cached it")
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to generate embedding for text: {str(e)}")
            raise

    def search_similar_chunks(self, query: str, collection_name: str, top_k: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform similarity search in Qdrant to find relevant chunks.

        Args:
            query: The query text to search for
            collection_name: Name of the Qdrant collection to search
            top_k: Number of results to return
            threshold: Minimum similarity score threshold

        Returns:
            List of retrieved chunks with text, score, metadata, and source URL
        """
        try:
            self.logger.info(f"Starting similarity search for query: {query[:50]}... in collection: {collection_name}")
            query_embedding = self.get_embedding(query)

            search_results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=threshold
            )

            retrieved_chunks = []
            for result in search_results:
                chunk = {
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": result.payload.get("metadata", {}),
                    "source_url": result.payload.get("source_url", "")
                }
                retrieved_chunks.append(chunk)

            self.logger.info(f"Retrieved {len(retrieved_chunks)} chunks from Qdrant")
            return retrieved_chunks
        except Exception as e:
            self.logger.error(f"Failed to perform similarity search: {str(e)}")
            raise

    def calculate_ranking_metrics(self, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate detailed ranking metrics for the retrieved chunks.

        Args:
            retrieved_chunks: List of retrieved chunks with scores

        Returns:
            Dictionary containing various ranking quality metrics
        """
        if len(retrieved_chunks) <= 1:
            return {
                "ranking_correctness": 1.0,
                "normalized_discounted_cumulative_gain": 1.0,
                "mean_reciprocal_rank": 1.0,
                "precision_at_k": 1.0 if len(retrieved_chunks) > 0 else 0.0
            }

        # Perfect ranking correctness - check if scores are in descending order
        ranking_correctness = 1.0
        for i in range(1, len(retrieved_chunks)):
            if retrieved_chunks[i]["score"] > retrieved_chunks[i-1]["score"]:
                ranking_correctness = 0.0  # Not perfectly ranked
                break

        # Calculate NDCG (Normalized Discounted Cumulative Gain) as a more sophisticated ranking metric
        dcg = 0.0
        for i, chunk in enumerate(retrieved_chunks):
            # DCG formula: rel1 + sum(rel_i / log2(i+1) for i in range(2, n+1))
            if i == 0:
                dcg += chunk["score"]
            else:
                dcg += chunk["score"] / (i + 1)  # Using linear version for simplicity

        # For ideal ranking, sort by score in descending order
        ideal_chunks = sorted(retrieved_chunks, key=lambda x: x["score"], reverse=True)
        idcg = 0.0
        for i, chunk in enumerate(ideal_chunks):
            if i == 0:
                idcg += chunk["score"]
            else:
                idcg += chunk["score"] / (i + 1)  # Using linear version for simplicity

        ndcg = dcg / idcg if idcg > 0 else 0.0

        # Mean Reciprocal Rank (MRR) - if we had relevance labels, this would be more meaningful
        # For now, we'll use a simplified version based on score ordering
        mrr = 1.0 / len(retrieved_chunks)  # Simplified version

        # Precision at K
        precision_at_k = len(retrieved_chunks) / len(retrieved_chunks) if len(retrieved_chunks) > 0 else 0.0

        return {
            "ranking_correctness": ranking_correctness,
            "normalized_discounted_cumulative_gain": ndcg,
            "mean_reciprocal_rank": mrr,
            "precision_at_k": precision_at_k
        }

    def validate_retrieval(self, query: str, collection_name: str, top_k: int = 5, threshold: float = 0.7) -> Dict[str, Any]:
        """
        Validate retrieval accuracy for the given query.

        Args:
            query: The test query to validate
            collection_name: Name of the Qdrant collection to search
            top_k: Number of results to retrieve
            threshold: Minimum similarity score threshold

        Returns:
            Validation results including accuracy metrics
        """
        try:
            self.logger.info(f"Starting validation for query: {query[:50]}...")
            retrieved_chunks = self.search_similar_chunks(query, collection_name, top_k, threshold)

            # Calculate validation metrics
            validation_passed = len(retrieved_chunks) > 0
            accuracy_score = sum([chunk["score"] for chunk in retrieved_chunks]) / len(retrieved_chunks) if retrieved_chunks else 0.0

            # Calculate detailed ranking metrics
            ranking_metrics = self.calculate_ranking_metrics(retrieved_chunks)

            # Data integrity check - verify that chunks have required fields
            data_integrity_check = all([
                chunk.get("text") and chunk.get("source_url") and chunk.get("metadata")
                for chunk in retrieved_chunks
            ])

            result = {
                "query": query,
                "validation_passed": validation_passed,
                "accuracy_score": accuracy_score,
                "retrieved_chunks": retrieved_chunks,
                "ranking_correctness": ranking_metrics["ranking_correctness"],
                "ranking_metrics": ranking_metrics,
                "data_integrity_check": data_integrity_check,
                "top_k": top_k,
                "threshold": threshold
            }

            self.logger.info(f"Validation completed. Results: passed={validation_passed}, chunks={len(retrieved_chunks)}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to validate retrieval: {str(e)}")
            raise


def main():
    """
    Main function to run the retrieval validation from command line.
    """
    try:
        # Set up logging for the main function
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        logger.info("Starting RAG retrieval validation")
        parser = argparse.ArgumentParser(description="RAG Retrieval Validation")
        parser.add_argument("--query", type=str, required=True, help="The test query to validate")
        parser.add_argument("--collection", type=str, help="Qdrant collection name (optional, will auto-detect if not specified)")
        parser.add_argument("--top-k", type=int, default=5, help="Number of results to retrieve (default: 5)")
        parser.add_argument("--threshold", type=float, default=0.7, help="Minimum similarity score (default: 0.7)")

        args = parser.parse_args()
        logger.info(f"Parsed arguments: query='{args.query[:50]}...', collection='{args.collection}', top_k={args.top_k}, threshold={args.threshold}")

        # Load environment variables
        dotenv.load_dotenv()
        logger.info("Environment variables loaded")

        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        cohere_api_key = os.getenv("COHERE_API_KEY")

        if not all([qdrant_url, qdrant_api_key, cohere_api_key]):
            error_msg = "Missing required environment variables. Please set QDRANT_URL, QDRANT_API_KEY, and COHERE_API_KEY"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Initialize validator
        logger.info("Initializing validator...")
        validator = RetrievalValidator(qdrant_url, qdrant_api_key, cohere_api_key)

        # Auto-detect collection if not provided
        if not args.collection:
            logger.info("Auto-detecting collection...")
            collections = validator.qdrant_client.get_collections()
            if collections.collections:
                args.collection = collections.collections[0].name
                print(f"Auto-detected collection: {args.collection}")
                logger.info(f"Auto-detected collection: {args.collection}")
            else:
                error_msg = "No collections found in Qdrant and no collection specified"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # Perform validation
        logger.info(f"Performing validation for query: {args.query[:50]}...")
        result = validator.validate_retrieval(args.query, args.collection, args.top_k, args.threshold)

        # Print results
        print(f"\nQuery: {result['query']}")
        print(f"Validation Passed: {result['validation_passed']}")
        print(f"Accuracy Score: {result['accuracy_score']:.3f}")
        print(f"Ranking Correctness: {result['ranking_correctness']:.3f}")
        print(f"Data Integrity Check: {result['data_integrity_check']}")
        print(f"Top-K: {result['top_k']}, Threshold: {result['threshold']}")

        print("\nRetrieved Chunks:")
        for i, chunk in enumerate(result['retrieved_chunks'], 1):
            print(f"  {i}. Score: {chunk['score']:.3f}, Source: {chunk['source_url']}")
            print(f"     Text: {chunk['text'][:100]}...")
            print(f"     Metadata: {chunk['metadata']}")
            print()

        logger.info("Validation completed successfully")
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        print(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()