#!/usr/bin/env python3
"""
Test script to verify Qdrant data retrieval with different parameters
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_qdrant_retrieval():
    """Test Qdrant data retrieval with various parameters"""
    try:
        print("Testing Qdrant data retrieval...")

        # Import and test the function directly
        from src.qdrant_client import retrieve_context_for_question

        # Test with different thresholds and top_k values
        test_queries = ["ROS", "robotics", "Qdrant", "documentation"]

        for query in test_queries:
            print(f"\n--- Testing query: '{query}' ---")

            # Try with lower threshold
            results = retrieve_context_for_question(
                question=query,
                top_k=5,
                threshold=0.1  # Lower threshold to get more results
            )

            print(f"Results count: {len(results)}")
            for i, result in enumerate(results):
                print(f"  Result {i+1}: Score={result.get('score', 'N/A')}")
                content_preview = result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', '')
                print(f"    Content: {content_preview}")

            if len(results) == 0:
                # Try with even lower threshold
                results = retrieve_context_for_question(
                    question=query,
                    top_k=10,
                    threshold=0.0  # Minimum threshold
                )
                print(f"With threshold 0.0: {len(results)} results")

    except Exception as e:
        print(f"Error during Qdrant retrieval test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_qdrant_retrieval()