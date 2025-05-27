
import os
import cohere
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from src.embedding.exceptions import InvalidAPIKeyException

load_dotenv(override=True)


class EmbeddingModel(ABC):
    """
    A base class for embedding models.

    Attributes:
        model_name (str): The name of the embedding model.
    """

    def __init__(self, model_name: str):
        """
        Initialize the embedding model.

        Args:
            model_name (str): The name of the embedding model.
        """
        self.model_name = model_name

    @abstractmethod
    async def generate_texts_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts (list[str]): A list of input texts.

        Returns:
            list[list[float]]: A list of embedding vectors for the input texts.
        """
        pass

    def __str__(self) -> str:
        """
        Return a string representation of the embedding model.

        Returns:
            str: The name of the embedding model.
        """
        return self.model_name


class CohereEmbeddingModel(EmbeddingModel):
    """
    A specific implementation of the EmbeddingModel that uses the Cohere API.

    Attributes:
        model (str): The name of the Cohere embedding model.
        api_key (str): The API key for the Cohere service.
        cohere (cohere.Client): The Cohere client instance.
        SEARCH_DOCUMENT_TYPE (str): The input type for the embedding model.
    """

    def __init__(self):
        """
        Initialize the Cohere embedding model.

        Args:
            api_key (str): The API key for the Cohere service. If not provided,
                           it will be loaded from the environment.
        """
        self.model = "embed-v4.0"
        model_name = f"cohere/{self.model}"
        super().__init__(model_name)
        self.api_key = CohereEmbeddingModel.get_api_key()   
        self.cohere = None
        self.SEARCH_DOCUMENT_TYPE = "search_query"

    @staticmethod
    async def create() -> "CohereEmbeddingModel":
        embedding_model = CohereEmbeddingModel()
        embedding_model.cohere = cohere.AsyncClient(api_key=embedding_model.api_key)
        return embedding_model

    @staticmethod
    def get_api_key() -> str:
        """
        Get the Cohere API key from the environment.

        Returns:
            str: The Cohere API key.

        Raises:
            InvalidAPIKeyException: If the API key is not found.
        """
        api_key = os.getenv("COHERE_API_KEY", None)
        if not api_key:
            raise InvalidAPIKeyException("Cohere API key is required.")
        return api_key

    
    async def generate_texts_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts using the Cohere API.

        Args:
            texts (list[str]): A list of input texts. The maximum number of texts is 96

        Returns:
            list[list[float]]: A list of embedding vectors for the input texts.

        Raises:
            Exception: If the API call fails.
        """
        if len(texts) > 96:
            raise ValueError("The maximum number of texts is 1000.")

        try:    

            res = await self.cohere.embed(
                texts=texts,
                model=self.model,
                input_type=self.SEARCH_DOCUMENT_TYPE,
                embedding_types=["float"],
            )
            return res.embeddings.float_
        except Exception as e:
            raise Exception(f"Failed to generate embeddings for texts: {e}")
