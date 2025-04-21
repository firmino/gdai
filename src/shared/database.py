import os
import weaviate
from dotenv import load_dotenv

load_dotenv()

class WeaviateDatabase:
    """
    A class for interacting with a Weaviate database using the async client.
    """

    @staticmethod
    async def get_client():
        """
        Get the Weaviate async client.
        """
        weaviate_url = os.environ.get("WEAVIATE_URL")
        if not weaviate_url:
            raise ValueError("WEAVIATE_URL environment variable not set.")
        
        client = weaviate.AsyncClient(
            url=weaviate_url,
            timeout_config=(5, 15),  # Optional: Configure timeouts (connect, read)
            startup_checks=False  # Skip gRPC health checks during initialization
        )
        return client
