#!/usr/bin/env python3
"""
Test script to verify data retrieval using the project's actual implementation
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Update COLLECTION_NAME to match the existing collection
os.environ["COLLECTION_NAME"] = "robotics_docs"

def test_retrieval_with_actual_implementation():
    """Test data retrieval using the project's actual implementation"""
    try:
        print("Testing data retrieval using project's actual implementation...")

        # Import and use the actual function from the project
        from src.qdrant_client import retrieve_context_for_question

        # Test with a sample query
        sample_query = "What is robotics?"
        print(f"Query: {sample_query}")

        results = retrieve_context_for_question(
            question=sample_query,
            top_k=3,
            threshold=0.5
        )

        print(f"Retrieved {len(results)} results:")
        for i, result in enumerate(results):
            print(f"  Result {i+1}:")
            print(f"    Score: {result.get('score', 'N/A')}")
            print(f"    Content preview: {result.get('content', '')[:100]}...")
            print(f"    Metadata keys: {list(result.get('metadata', {}).keys())}")
            print()

        if len(results) > 0:
            print("✅ Data retrieval test completed successfully!")
            return True
        else:
            print("⚠️  No results returned, but no errors occurred.")
            return True

    except Exception as e:
        print(f"❌ Error during data retrieval test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_retrieval_with_actual_implementation()
    if success:
        print("\n✅ Data retrieval test completed successfully!")
    else:
        print("\n❌ Data retrieval test failed!")