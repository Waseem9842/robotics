import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentConfig:
    """
    Configuration utility to manage agent settings from environment variables
    """

    def __init__(self):
        self.model = os.getenv("MODEL_NAME", "mistralai/devstral-2512:free")
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        self.top_k = int(os.getenv("TOP_K", "5"))
        self.grounding_threshold = float(os.getenv("GROUNDING_THRESHOLD", "0.5"))
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("COLLECTION_NAME", "documents")

    def get_openai_config(self):
        """
        Get OpenAI-specific configuration
        """
        return {
            "model": self.model,
            "temperature": self.temperature
        }

    def get_qdrant_config(self):
        """
        Get Qdrant-specific configuration
        """
        return {
            "url": self.qdrant_url,
            "api_key": self.qdrant_api_key,
            "collection_name": self.collection_name
        }

    def get_retrieval_config(self):
        """
        Get retrieval-specific configuration
        """
        return {
            "top_k": self.top_k,
            "threshold": self.grounding_threshold
        }

# Global configuration instance
config = AgentConfig()