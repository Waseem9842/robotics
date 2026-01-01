"""
Test script to verify the API endpoint works correctly
"""
import asyncio
import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test the API endpoints to verify integration"""
    base_url = "http://localhost:8000"

    print("Testing API endpoints...")

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ Health check passed: {health_data['status']}")
        else:
            print(f"✗ Health check failed with status: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {str(e)}")

    # Test query endpoint
    try:
        query_payload = {
            "query": "What is the purpose of this RAG system?"
        }

        response = requests.post(
            f"{base_url}/api/query",
            json=query_payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            query_data = response.json()
            print(f"✓ Query endpoint test passed")
            print(f"  Response: {query_data['response'][:100]}...")
            print(f"  Status: {query_data['status']}")
        else:
            print(f"✗ Query endpoint test failed with status: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Query endpoint test error: {str(e)}")

    print("\nAPI testing completed.")

if __name__ == "__main__":
    test_api_endpoints()