#!/usr/bin/env python3
"""
Test script to verify Qdrant database connection
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

# Load environment variables
load_dotenv()

def test_qdrant_connection():
    """Test the Qdrant connection"""
    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=10
        )

        print("Attempting to connect to Qdrant...")

        # Try to get collections list to verify connection
        collections = client.get_collections()
        print(f"Connected successfully! Available collections: {collections}")

        # Check if the expected collection exists
        collection_name = os.getenv("COLLECTION_NAME", "your_collection_name")
        print(f"Looking for collection: {collection_name}")

        # If collection doesn't exist, create it with appropriate vector size
        # (This is just a test - in real usage, you'd need the correct vector size)
        try:
            collection_info = client.get_collection(collection_name)
            print(f"Collection '{collection_name}' exists with {collection_info.points_count} points")
        except Exception as e:
            print(f"Collection '{collection_name}' doesn't exist or error getting info: {e}")
            print("This might be expected if no data has been ingested yet.")

        return True

    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        return False

if __name__ == "__main__":
    print("Testing Qdrant database connection...")
    success = test_qdrant_connection()
    if success:
        print("Database connection test completed successfully!")
    else:
        print("Database connection test failed!")