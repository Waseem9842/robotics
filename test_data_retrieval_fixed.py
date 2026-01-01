#!/usr/bin/env python3
"""
Test script to verify data retrieval from Qdrant database
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import numpy as np

# Load environment variables
load_dotenv()

def test_data_retrieval():
    """Test data retrieval from Qdrant"""
    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=10
        )

        print("Testing data retrieval from Qdrant...")

        # Check the existing collection
        collection_name = "robotics_docs"  # Based on what we found earlier
        print(f"Checking collection: {collection_name}")

        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists with {collection_info.points_count} points")

        # Print vector configuration
        print(f"Vector config: {collection_info.config.params}")

        if collection_info.points_count > 0:
            # Get a few sample points to verify data structure
            sample_points = client.scroll(
                collection_name=collection_name,
                limit=2,
                with_payload=True
            )

            print(f"Sample points retrieved: {len(sample_points[0])}")
            for i, point in enumerate(sample_points[0]):
                print(f"Point {i+1}:")
                print(f"  ID: {point.id}")
                print(f"  Payload keys: {list(point.payload.keys()) if point.payload else 'None'}")
                if point.payload:
                    # Print a sample of the payload content
                    for key, value in list(point.payload.items())[:3]:  # Show first 3 keys
                        print(f"    {key}: {str(value)[:100]}...")  # Limit to 100 chars
                print()
        else:
            print("No points found in the collection.")

        # Test a simple search with a dummy query vector (just to test the search functionality)
        # We'll create a dummy vector of the same size as expected by the collection
        # For now, let's try to get one point to see its vector size
        if collection_info.points_count > 0:
            # Get first point to check vector size - using the correct API
            first_points = client.scroll(
                collection_name=collection_name,
                limit=1,
                with_payload=False
            )

            # Get point by ID to access the vector
            if first_points[0]:
                first_point_id = first_points[0][0].id
                point_info = client.retrieve(
                    collection_name=collection_name,
                    ids=[first_point_id],
                    with_payload=False,
                    with_vectors=True
                )

                if point_info:
                    vector_size = len(point_info[0].vector)
                    print(f"Vector size: {vector_size}")

                    # Now test search with a dummy vector of the same size
                    dummy_query_vector = [0.0] * vector_size  # Simple dummy vector

                    search_results = client.search(
                        collection_name=collection_name,
                        query_vector=dummy_query_vector,
                        limit=3,
                        with_payload=True
                    )

                    print(f"Search test results: {len(search_results)} items returned")
                    for i, result in enumerate(search_results):
                        print(f"  Result {i+1}: Score={result.score}, ID={result.id}")
                        if result.payload:
                            print(f"    Content preview: {str(result.payload.get('content', ''))[:100]}...")

        return True

    except Exception as e:
        print(f"Error during data retrieval test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing data retrieval from Qdrant database...")
    success = test_data_retrieval()
    if success:
        print("Data retrieval test completed successfully!")
    else:
        print("Data retrieval test failed!")