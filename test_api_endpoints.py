#!/usr/bin/env python3
"""
Test script to verify the FastAPI chatbot endpoints
"""
import requests
import json
import time

def test_fastapi_endpoints():
    """Test the FastAPI endpoints"""
    base_url = "http://localhost:8000"

    print("Testing FastAPI endpoints...")

    # Test the root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data}")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing root endpoint: {e}")

    # Test the health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data}")
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

    # Test the query endpoint with a sample query
    # Note: This might fail due to the OpenAI quota issue we saw earlier,
    # but we can still test if the endpoint is accessible
    try:
        query_data = {
            "query": "What is robotics?",
            "session_id": None
        }
        response = requests.post(f"{base_url}/api/query",
                                json=query_data,
                                headers={"Content-Type": "application/json"})

        print(f"Query endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query endpoint response: {json.dumps(data, indent=2)[:500]}...")
        elif response.status_code == 500:
            error_data = response.json()
            print(f"⚠️  Query endpoint returned error (expected due to API quota): {error_data}")
        else:
            print(f"❌ Query endpoint failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error testing query endpoint: {e}")

if __name__ == "__main__":
    print("Testing FastAPI chatbot endpoints...")
    test_fastapi_endpoints()
    print("\nAPI endpoint testing completed!")