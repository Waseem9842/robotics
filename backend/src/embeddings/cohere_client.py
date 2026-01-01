"""Module for interacting with Cohere API for embedding generation."""

import cohere
from typing import List, Dict, Any, Union
from src.config import Config
from src.exceptions import EmbeddingGenerationError, ConfigurationError
from src.utils.logger import app_logger


class CohereClient:
    """Class to handle interactions with Cohere API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the Cohere client.

        Args:
            api_key: Cohere API key (defaults to using config value)
        """
        self.api_key = api_key or Config.COHERE_API_KEY

        if not self.api_key:
            raise ConfigurationError("Cohere API key is required")

        try:
            self.client = cohere.Client(self.api_key)
        except Exception as e:
            app_logger.error(f"Failed to initialize Cohere client: {str(e)}")
            raise ConfigurationError(f"Failed to initialize Cohere client: {str(e)}")

    def generate_embeddings(
        self,
        texts: List[str],
        model: str = "embed-english-v3.0",
        input_type: str = "search_document"
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for
            model: Cohere model to use for embeddings
            input_type: Type of input (affects how the model processes the text)

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        try:
            app_logger.info(f"Generating embeddings for {len(texts)} texts using model: {model}")
            response = self.client.embed(
                texts=texts,
                model=model,
                input_type=input_type
            )

            embeddings = [embedding for embedding in response.embeddings]
            app_logger.info(f"Successfully generated {len(embeddings)} embeddings")

            return embeddings

        except Exception as e:
            app_logger.error(f"Error generating embeddings: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {str(e)}")

    def generate_single_embedding(
        self,
        text: str,
        model: str = "embed-english-v3.0",
        input_type: str = "search_document"
    ) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to generate embedding for
            model: Cohere model to use for embeddings
            input_type: Type of input (affects how the model processes the text)

        Returns:
            Embedding vector
        """
        if not text:
            raise EmbeddingGenerationError("Text cannot be empty")

        try:
            embeddings = self.generate_embeddings([text], model, input_type)
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            else:
                raise EmbeddingGenerationError("No embeddings returned from Cohere API")
        except Exception as e:
            app_logger.error(f"Error generating single embedding: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate single embedding: {str(e)}")

    def validate_api_connection(self) -> bool:
        """
        Validate that the Cohere API connection is working.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Test with a simple embedding request
            test_embedding = self.generate_single_embedding("test")
            return len(test_embedding) > 0
        except Exception as e:
            app_logger.error(f"API connection validation failed: {str(e)}")
            return False

    def get_model_info(self, model: str = "embed-english-v3.0") -> Dict[str, Any]:
        """
        Get information about a specific model.

        Args:
            model: Model name to get info for

        Returns:
            Model information
        """
        # Note: Cohere doesn't have a direct API for model info, so we'll return basic info
        model_info = {
            "model_name": model,
            "dimensions": "variable",  # This will vary by model
            "type": "embedding",
            "recommended_use": "text embedding for semantic search"
        }
        return model_info


# For command-line usage
def main():
    """Command-line interface for testing Cohere client."""
    import argparse

    parser = argparse.ArgumentParser(description='Test Cohere embedding generation')
    parser.add_argument('--text', type=str, required=True, help='Text to embed')
    args = parser.parse_args()

    try:
        client = CohereClient()
        embedding = client.generate_single_embedding(args.text)
        print(f"Generated embedding with {len(embedding)} dimensions")
        print(f"First 5 dimensions: {embedding[:5]}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()