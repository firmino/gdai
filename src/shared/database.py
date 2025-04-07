import os
import weaviate
import WeaviateClient


class WeaviateDatabase:
    """
    A class for interacting with a Weaviate database.
    """

    @staticmethod
    def get_client() -> WeaviateClient:
        """
        Get the Weaviate client.
        """
        weaviate_url = os.environ.get("WEAVIATE_URL")
        client = weaviate.connect_to_local(hots=weaviate_url)
        return client
