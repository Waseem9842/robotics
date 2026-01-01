"""Module for generating embeddings with Cohere."""

from typing import List, Dict, Any
from src.embeddings.cohere_client import CohereClient
from src.models.book_content import BookContent
from src.models.embedding_vector import EmbeddingVector
from src.utils.id_generator import generate_embedding_id
from src.utils.logger import app_logger
from src.exceptions import EmbeddingGenerationError, ValidationError
from src.config import Config


class EmbeddingGenerator:
    """Class to generate embeddings from content."""

    def __init__(
        self,
        cohere_api_key: str = None,
        model: str = "embed-english-v3.0",
        input_type: str = "search_document"
    ):
        """
        Initialize the embedding generator.

        Args:
            cohere_api_key: Cohere API key (defaults to config)
            model: Cohere model to use for embeddings
            input_type: Type of input for the model
        """
        self.cohere_client = CohereClient(cohere_api_key)
        self.model = model
        self.input_type = input_type

    def generate_from_text(self, text: str) -> EmbeddingVector:
        """
        Generate an embedding vector from a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            EmbeddingVector instance
        """
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty")

        try:
            # Generate the embedding
            embedding_vector = self.cohere_client.generate_single_embedding(
                text=text,
                model=self.model,
                input_type=self.input_type
            )

            # Generate a unique ID for this embedding
            content_id = generate_embedding_id("text_content", self.model)

            # Create EmbeddingVector instance
            embedding_obj = EmbeddingVector.create(
                id=content_id,
                vector=embedding_vector,
                content_id="text_content",  # Placeholder, should be set based on actual content
                model_name=self.model
            )

            app_logger.info(f"Generated embedding for text, ID: {content_id}")
            return embedding_obj

        except Exception as e:
            app_logger.error(f"Error generating embedding for text: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")

    def generate_from_content(self, content: BookContent) -> EmbeddingVector:
        """
        Generate an embedding vector from BookContent.

        Args:
            content: BookContent instance to generate embedding for

        Returns:
            EmbeddingVector instance
        """
        if not content or not content.content.strip():
            raise ValidationError("Content cannot be empty")

        try:
            # Generate the embedding
            embedding_vector = self.cohere_client.generate_single_embedding(
                text=content.content,
                model=self.model,
                input_type=self.input_type
            )

            # Generate a unique ID for this embedding based on content ID
            embedding_id = generate_embedding_id(content.id, self.model)

            # Create EmbeddingVector instance
            embedding_obj = EmbeddingVector.create(
                id=embedding_id,
                vector=embedding_vector,
                content_id=content.id,
                model_name=self.model
            )

            app_logger.info(f"Generated embedding for content ID {content.id}, embedding ID: {embedding_id}")
            return embedding_obj

        except Exception as e:
            app_logger.error(f"Error generating embedding for content {content.id}: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate embedding for content {content.id}: {str(e)}")

    def generate_batch_from_texts(self, texts: List[str]) -> List[EmbeddingVector]:
        """
        Generate embedding vectors for a batch of texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of EmbeddingVector instances
        """
        if not texts:
            return []

        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return []

        try:
            # Generate embeddings for all texts at once
            embedding_vectors = self.cohere_client.generate_embeddings(
                texts=valid_texts,
                model=self.model,
                input_type=self.input_type
            )

            # Create EmbeddingVector instances
            embedding_objects = []
            for i, (text, vector) in enumerate(zip(valid_texts, embedding_vectors)):
                content_id = generate_embedding_id(f"text_content_{i}", self.model)
                embedding_obj = EmbeddingVector.create(
                    id=content_id,
                    vector=vector,
                    content_id=f"text_content_{i}",
                    model_name=self.model
                )
                embedding_objects.append(embedding_obj)

            app_logger.info(f"Generated {len(embedding_objects)} embeddings for batch of {len(valid_texts)} texts")
            return embedding_objects

        except Exception as e:
            app_logger.error(f"Error generating batch embeddings: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate batch embeddings: {str(e)}")

    def generate_batch_from_contents(self, contents: List[BookContent]) -> List[EmbeddingVector]:
        """
        Generate embedding vectors for a batch of BookContent instances.

        Args:
            contents: List of BookContent instances to generate embeddings for

        Returns:
            List of EmbeddingVector instances
        """
        if not contents:
            return []

        # Filter out contents with empty text
        valid_contents = [content for content in contents if content.content and content.content.strip()]
        if not valid_contents:
            return []

        try:
            # Extract texts from contents
            texts = [content.content for content in valid_contents]

            # Generate embeddings for all texts at once
            embedding_vectors = self.cohere_client.generate_embeddings(
                texts=texts,
                model=self.model,
                input_type=self.input_type
            )

            # Create EmbeddingVector instances
            embedding_objects = []
            for content, vector in zip(valid_contents, embedding_vectors):
                embedding_id = generate_embedding_id(content.id, self.model)
                embedding_obj = EmbeddingVector.create(
                    id=embedding_id,
                    vector=vector,
                    content_id=content.id,
                    model_name=self.model
                )
                embedding_objects.append(embedding_obj)

            app_logger.info(f"Generated {len(embedding_objects)} embeddings for batch of {len(valid_contents)} contents")
            return embedding_objects

        except Exception as e:
            app_logger.error(f"Error generating batch embeddings from contents: {str(e)}")
            raise EmbeddingGenerationError(f"Failed to generate batch embeddings from contents: {str(e)}")

    def validate_embedding(self, embedding: EmbeddingVector) -> bool:
        """
        Validate that an embedding meets quality requirements.

        Args:
            embedding: EmbeddingVector to validate

        Returns:
            True if valid, False otherwise
        """
        if not embedding or not embedding.vector:
            return False

        # Check that vector has reasonable dimensions (not too small)
        if len(embedding.vector) < 10:
            return False

        # Check that vector contains valid numbers (not all zeros or NaN)
        if all(v == 0.0 for v in embedding.vector):
            return False

        # Check for NaN or infinity values
        import math
        if any(math.isnan(v) or math.isinf(v) for v in embedding.vector):
            return False

        return True

    def run(self, contents: List[BookContent]) -> List[EmbeddingVector]:
        """
        Run the embedding generation pipeline on a list of contents.

        Args:
            contents: List of BookContent instances to process

        Returns:
            List of EmbeddingVector instances
        """
        app_logger.info(f"Starting embedding generation for {len(contents)} contents")

        try:
            # Generate embeddings in batch
            embeddings = self.generate_batch_from_contents(contents)

            # Validate embeddings
            valid_embeddings = [emb for emb in embeddings if self.validate_embedding(emb)]
            invalid_count = len(embeddings) - len(valid_embeddings)

            if invalid_count > 0:
                app_logger.warning(f"Generated {invalid_count} invalid embeddings out of {len(embeddings)} total")

            app_logger.info(f"Completed embedding generation, {len(valid_embeddings)} valid embeddings")
            return valid_embeddings

        except Exception as e:
            app_logger.error(f"Embedding generation pipeline failed: {str(e)}")
            raise EmbeddingGenerationError(f"Embedding generation pipeline failed: {str(e)}")


# For command-line usage
def main():
    """Command-line interface for the embedding generator."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Embedding generation pipeline')
    parser.add_argument('--text', type=str, required=True, help='Text to generate embedding for')
    args = parser.parse_args()

    try:
        generator = EmbeddingGenerator()
        embedding = generator.generate_from_text(args.text)
        print(f"Generated embedding with {len(embedding.vector)} dimensions")
        print(f"Embedding ID: {embedding.id}")
    except Exception as e:
        app_logger.error(f"Error in command-line embedding generation: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()