import os
import pytest
from dotenv import load_dotenv
from src.embedding_pipeline.exceptions import InvalidAPIKeyException
from src.embedding_pipeline.embedding import CohereEmbeddingModel


class TestEmbeddingModel:

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:cohere.*")
    @pytest.mark.asyncio(loop_scope="module")
    async def test_generate_text_embedding_cohere(self):
        load_dotenv()
        embedding_model = await CohereEmbeddingModel.create()
        embedding = await embedding_model.generate_texts_embeddings(["Hello, world!"])
        assert isinstance(embedding, list)
        assert len(embedding[0]) == 1536

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:cohere.*")
    @pytest.mark.asyncio(loop_scope="module")
    async def test_invalid_number_of_batch_text_to_embedding(self):
        load_dotenv()
        embedding_model = await CohereEmbeddingModel.create()
        with pytest.raises(ValueError):
            await embedding_model.generate_texts_embeddings(["Hello, world!"] * 100)

    @pytest.mark.filterwarnings("ignore::DeprecationWarning:cohere.*")
    @pytest.mark.asyncio(loop_scope="module")
    async def test_generate_text_embedding_cohere_with_wrong_key(self):
        os.environ.pop("COHERE_API_KEY", None)
        with pytest.raises(InvalidAPIKeyException):
            embedding_model = await CohereEmbeddingModel.create()
            await embedding_model.generate_text_embedding("Hello, world!")
