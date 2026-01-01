import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchRequest
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()

class QdrantClientUtility:
    """
    Utility class to interface with existing Qdrant retrieval pipeline
    """

    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=10
        )
        self.collection_name = os.getenv("COLLECTION_NAME", "documents")

    def search(self, query_text: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in Qdrant based on the query text
        """
        try:
            # Use the same embedding model (Cohere) that was used to create the stored vectors
            import cohere
            import os
            import time
            from dotenv import load_dotenv
            load_dotenv()  # Load environment variables

            # Initialize Cohere client directly using the API key from environment
            cohere_api_key = os.getenv("COHERE_API_KEY")
            if not cohere_api_key:
                print("Error: COHERE_API_KEY not found in environment variables")
                return []

            cohere_client = cohere.Client(cohere_api_key)

            # Attempt to generate embedding with retries for rate limiting
            max_retries = 3
            retry_delay = 1  # Start with 1 second

            for attempt in range(max_retries):
                try:
                    response = cohere_client.embed(
                        texts=[query_text],
                        model="embed-english-v3.0",  # Same model used for stored vectors
                        input_type="search_query"  # Using search_query type for queries vs search_document for stored docs
                    )

                    query_embedding = response.embeddings[0]
                    break  # Success, break out of retry loop

                except cohere.errors.TooManyRequestsError:
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        print(f"Cohere API rate limit exceeded after {max_retries} attempts")
                        return []
                    else:
                        # Wait before retry with exponential backoff
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Cohere API rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)

                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Error generating embedding after {max_retries} attempts: {e}")
                        return []
                    else:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Embedding generation failed, waiting {wait_time}s before retry {attempt + 1}/{max_retries}: {e}")
                        time.sleep(wait_time)

            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,  # Pass the embedding as the query parameter
                limit=top_k,
                score_threshold=threshold
            )

            results = []
            for hit in search_result:
                result = {
                    "content": hit.payload.get("content", "") if hit.payload else "",
                    "metadata": hit.payload or {},
                    "score": hit.score,
                    "source_documents": [hit.id]
                }
                results.append(result)

            return results
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_relevant_context(self, question: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get relevant context for a given question
        """
        return self.search(question, top_k, threshold)


def retrieve_context_for_question(question: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Standalone function that queries Qdrant based on user question
    """
    client_utility = QdrantClientUtility()
    return client_utility.get_relevant_context(question, top_k, threshold)