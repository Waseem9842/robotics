"""Main entry point for the embeddings vector storage pipeline."""

import argparse
import sys
from typing import List, Dict, Any
from src.ingestion.pipeline import ContentExtractionPipeline
from src.embeddings.generator import EmbeddingGenerator
from src.storage.vector_store import VectorStore
from src.storage.verification import VerificationService
from src.config import Config
from src.utils.logger import app_logger
from src.models.book_content import BookContent
from src.models.embedding_vector import EmbeddingVector


def main():
    """Main function to run the full ingestion pipeline."""
    parser = argparse.ArgumentParser(description='URL ingestion and embedding pipeline')
    parser.add_argument('--urls', nargs='+', required=True, help='URLs to process')
    parser.add_argument('--chunk-size', type=int, default=Config.CHUNK_SIZE, help='Size of text chunks')
    parser.add_argument('--chunk-overlap', type=int, default=Config.CHUNK_OVERLAP, help='Overlap between chunks')
    parser.add_argument('--model', type=str, default='embed-english-v3.0', help='Cohere model to use')
    parser.add_argument('--verify', action='store_true', help='Run verification after storage')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode with limited processing')

    args = parser.parse_args()

    try:
        # Validate configuration
        Config.validate()
        app_logger.info("Configuration validated successfully")

        # Initialize components
        app_logger.info("Initializing pipeline components...")
        extraction_pipeline = ContentExtractionPipeline(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        embedding_generator = EmbeddingGenerator(model=args.model)
        vector_store = VectorStore()

        # Run content extraction
        app_logger.info(f"Starting content extraction from {len(args.urls)} URLs")
        extraction_result = extraction_pipeline.run(args.urls)
        contents: List[BookContent] = extraction_result['contents']
        stats = extraction_result['stats']

        app_logger.info(f"Content extraction completed. Stats: {stats}")
        if not contents:
            app_logger.error("No content extracted from provided URLs")
            sys.exit(1)

        # Generate embeddings
        app_logger.info(f"Starting embedding generation for {len(contents)} content chunks")
        embeddings: List[EmbeddingVector] = embedding_generator.run(contents)
        app_logger.info(f"Embedding generation completed. Generated {len(embeddings)} embeddings")

        if not embeddings:
            app_logger.error("No embeddings generated")
            sys.exit(1)

        # Store embeddings
        app_logger.info(f"Starting vector storage for {len(embeddings)} embeddings")
        storage_success = vector_store.run(embeddings, contents)
        if not storage_success:
            app_logger.error("Vector storage failed")
            sys.exit(1)
        app_logger.info("Vector storage completed successfully")

        # Verification (if requested)
        if args.verify:
            app_logger.info("Starting verification...")
            verification_service = VerificationService(vector_store)

            if args.test_mode:
                # Use a subset for testing
                test_embeddings = embeddings[:min(5, len(embeddings))]
                test_contents = contents[:min(5, len(contents))]
            else:
                test_embeddings = embeddings
                test_contents = contents

            verification_result = verification_service.run_comprehensive_verification(
                test_embeddings=test_embeddings,
                test_contents=test_contents
            )

            app_logger.info(f"Verification completed. Success: {verification_result.get('overall_success', False)}")

            if not verification_result.get('overall_success', False):
                app_logger.warning("Verification did not pass all checks")

        # Final summary
        app_logger.info("Pipeline completed successfully!")
        print(f"\nPipeline Summary:")
        print(f"- URLs processed: {stats['total_urls_processed']}")
        print(f"- Content chunks extracted: {stats['total_content_chunks']}")
        print(f"- Embeddings generated: {len(embeddings)}")
        print(f"- Storage: Successful")
        if args.verify:
            print(f"- Verification: {'Passed' if verification_result.get('overall_success', False) else 'Failed (or partial)'}")

    except KeyboardInterrupt:
        app_logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        app_logger.error(f"Pipeline failed with error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def run_pipeline(urls: List[str], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run the full pipeline programmatically.

    Args:
        urls: List of URLs to process
        config: Optional configuration parameters

    Returns:
        Dictionary with pipeline results
    """
    if config is None:
        config = {}

    # Use defaults or provided config values
    chunk_size = config.get('chunk_size', Config.CHUNK_SIZE)
    chunk_overlap = config.get('chunk_overlap', Config.CHUNK_OVERLAP)
    model = config.get('model', 'embed-english-v3.0')
    verify = config.get('verify', False)

    try:
        # Validate configuration
        Config.validate()

        # Initialize components
        extraction_pipeline = ContentExtractionPipeline(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        embedding_generator = EmbeddingGenerator(model=model)
        vector_store = VectorStore()

        # Run content extraction
        app_logger.info(f"Starting content extraction from {len(urls)} URLs")
        extraction_result = extraction_pipeline.run(urls)
        contents: List[BookContent] = extraction_result['contents']
        extraction_stats = extraction_result['stats']

        if not contents:
            return {'error': 'No content extracted from provided URLs', 'success': False}

        # Generate embeddings
        app_logger.info(f"Starting embedding generation for {len(contents)} content chunks")
        embeddings: List[EmbeddingVector] = embedding_generator.run(contents)

        if not embeddings:
            return {'error': 'No embeddings generated', 'success': False}

        # Store embeddings
        app_logger.info(f"Starting vector storage for {len(embeddings)} embeddings")
        storage_success = vector_store.run(embeddings, contents)
        if not storage_success:
            return {'error': 'Vector storage failed', 'success': False}

        # Verification (if requested)
        verification_result = None
        if verify:
            verification_service = VerificationService(vector_store)
            verification_result = verification_service.run_comprehensive_verification(
                test_embeddings=embeddings,
                test_contents=contents
            )

        # Return results
        results = {
            'success': True,
            'extraction_stats': extraction_stats,
            'embedding_count': len(embeddings),
            'storage_success': storage_success,
            'verification_result': verification_result
        }

        app_logger.info("Pipeline completed successfully")
        return results

    except Exception as e:
        app_logger.error(f"Pipeline failed with error: {str(e)}")
        return {'error': str(e), 'success': False}


if __name__ == "__main__":
    main()