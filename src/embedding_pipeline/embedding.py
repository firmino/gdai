"""
embedding.py

This module provides classes and methods for generating text embeddings using
various embedding models. It includes a base class for embedding models and
a specific implementation for the Cohere embedding model.

Classes:
    EmbeddingModel:
        A base class for embedding models. It defines the interface for
        embedding single or multiple texts.

    CohereEmbeddingModel:
        A specific implementation of the EmbeddingModel that uses the Cohere
        API to generate embeddings.

Usage:
    The `EmbeddingModel` class is intended to be subclassed by specific
    embedding model implementations. The `CohereEmbeddingModel` provides
    an example of such an implementation.

Example:
    >>> from embedding import CohereEmbeddingModel
    >>> model = CohereEmbeddingModel()
    >>> embedding = await model.embed_text("Sample text")
    >>> embeddings = await model.embed_texts(["Text 1", "Text 2"])
    >>> print(model)
    cohere/embed-english-v3.0
"""

import os
import cohere
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from src.embedding_pipeline.exceptions import InvalidAPIKeyException

load_dotenv()


class EmbeddingModel(ABC):
    """
    A base class for embedding models.

    Attributes:
        model_name (str): The name of the embedding model.
    """

    def __init__(self, model_name):
        """
        Initialize the embedding model.

        Args:
            model_name (str): The name of the embedding model.
        """
        self.model_name = model_name

    @abstractmethod
    async def generate_text_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text.

        Args:
            text (str): The input text.

        Returns:
            list[float]: The embedding vector for the input text.
        """
        pass

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

    def __str__(self):
        """
        Return a string representation of the embedding model.

        Returns:
            str: The name of the embedding model.
        """
        return self.model_name



class CohereEmbeddingModel(EmbeddingModel):
    """
    A specific implementation of the EmbeddingModel that uses the Cohere API.
    """
    def __init__(self, api_key: str = None):
        """
        Initialize the Cohere embedding model.

        Args:
            api_key (str): The API key for the Cohere service.
        """
        self.model = "embed-english-v3.0"
        model_name = f"cohere/{self.model}"
        super().__init__(model_name)
        self.api_key = api_key or CohereEmbeddingModel.get_api_key()
        self.cohere = cohere.Client(api_key=self.api_key)
        self.SEARCH_DOCUMENT_TYPE = "search_document"

    @staticmethod
    def get_api_key() -> str:
        """
        Get the Cohere API key from the environment.

        Returns:
            str: The Cohere API key.

        Raises:
            InvalidAPIKeyException: If the API key is not found.
        """
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise InvalidAPIKeyException("Cohere API key is required.")
        return api_key

    async def generate_text_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for a single text using the Cohere API.

        Args:
            text (str): The input text.

        Returns:
            list[float]: The embedding vector for the input text.

        Raises:
            Exception: If the API call fails.
        """

        #TODO: add async call to cohere
        try:
            res = self.cohere.embed( 
                texts=[text],
                model=self.model,
                input_type=self.SEARCH_DOCUMENT_TYPE,
                embedding_types=["float"],
            )
            return res.embeddings.float_[0]
        except Exception as e:
            raise Exception(f"Failed to generate embedding for text '{text}': {e}")

    async def generate_texts_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts using the Cohere API.

        Args:
            texts (list[str]): A list of input texts.

        Returns:
            list[list[float]]: A list of embedding vectors for the input texts.

        Raises:
            Exception: If the API call fails.
        """
        try:
            res = self.cohere.embed(
                texts=texts,
                model=self.model,
                input_type=self.SEARCH_DOCUMENT_TYPE,
                embedding_types=["float"],
            )
            return res.embeddings.float_
        except Exception as e:
            raise Exception(f"Failed to generate embeddings for texts: {e}")
