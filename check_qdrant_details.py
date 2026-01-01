#!/usr/bin/env python3
"""
Script to check the Qdrant client method signatures
"""
import inspect
from qdrant_client import QdrantClient

# Get the signature of the query method
try:
    sig = inspect.signature(QdrantClient.query)
    print(f"QdrantClient.query signature: {sig}")
except Exception as e:
    print(f"Error getting query signature: {e}")

# Check if search method exists and its signature
try:
    sig = inspect.signature(QdrantClient.search)
    print(f"QdrantClient.search signature: {sig}")
except Exception as e:
    print(f"search method not found or error: {e}")

# Check the actual methods that exist
client_methods = [method for method in dir(QdrantClient) if not method.startswith('_')]
print("\nAll public methods in QdrantClient:")
for method in sorted(client_methods):
    print(f"  - {method}")