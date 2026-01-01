#!/usr/bin/env python3
"""
Script to check the correct Qdrant API method names
"""
from qdrant_client import QdrantClient
import inspect

# Create a client instance to check available methods
client = QdrantClient(url="https://example.com", api_key="dummy")

# List methods that contain 'search' in their name
methods = [method for method in dir(client) if 'search' in method.lower()]
print("Available search-related methods:")
for method in methods:
    print(f"  - {method}")

# Check the most common search method
if hasattr(client, 'search'):
    print("\nThe 'search' method exists!")
else:
    print("\nThe 'search' method does NOT exist!")

# Also check for other possible methods
other_methods = ['search', 'query', 'retrieve', 'get_points', 'scroll']
print(f"\nChecking for these methods: {other_methods}")
for method in other_methods:
    exists = hasattr(client, method)
    print(f"  - {method}: {'✓' if exists else '✗'}")