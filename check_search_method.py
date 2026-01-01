#!/usr/bin/env python3
"""
Script to check the correct Qdrant search method
"""
import qdrant_client
from qdrant_client import QdrantClient

# Check if search method exists on the instance
client = QdrantClient(":memory:")  # Create in-memory client for testing

# Check if search is available in the client instance
has_search = hasattr(client, 'search')
print(f"Has search method: {has_search}")

# Check if query_points is available (which is likely what we want for vector search)
has_query_points = hasattr(client, 'query_points')
print(f"Has query_points method: {has_query_points}")

# Let's also check for the old search method that might be available
if has_search:
    import inspect
    sig = inspect.signature(client.search)
    print(f"search signature: {sig}")

if has_query_points:
    import inspect
    sig = inspect.signature(client.query_points)
    print(f"query_points signature: {sig}")

# Let's also check the http interface
has_http = hasattr(client, 'http')
if has_http:
    print(f"Has http interface: {has_http}")
    if hasattr(client.http, 'search'):
        print("http.search exists")
    else:
        print("http.search does NOT exist")