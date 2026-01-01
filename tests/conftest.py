import pytest
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Load environment variables for tests
load_dotenv()

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('agent.OpenAI') as mock:
        yield mock

@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing"""
    with patch('src.qdrant_client.QdrantClient') as mock:
        yield mock

@pytest.fixture
def sample_context():
    """Sample context data for testing"""
    return [
        {
            "content": "This is sample context content for testing purposes.",
            "metadata": {"source": "test_document", "page": 1},
            "score": 0.85,
            "source_documents": ["doc_123"]
        }
    ]

@pytest.fixture
def sample_question():
    """Sample question for testing"""
    return "What is the main topic of the document?"

@pytest.fixture
def agent_config():
    """Configuration for testing"""
    return {
        "model": "gpt-4-test",
        "temperature": 0.1,
        "top_k": 5,
        "grounding_threshold": 0.5
    }