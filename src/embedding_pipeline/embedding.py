import os
import cohere
from dotenv import load_dotenv


load_dotenv()


class EmbeddingModel:
    def __init__(self, model_name):
        self.model_name = model_name

    async def embed_text(self, text: str) -> list[float]:
        pass

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        pass

    def __str__(self):
        return self.model_name


class CohereEmbeddingModel(EmbeddingModel):
    def __init__(self):
        self.model = "embed-english-v3.0"
        model_name = f"cohere/{self.model}"
        super().__init__(model_name)
        API_KEY = os.getenv("COHERE_API_KEY")
        self.cohere = cohere.Client(api_key=API_KEY)

    async def embed_text(self, text: str) -> list[float]:
        input_type = "search_document"
        res = self.cohere.embed(
            texts=[text],
            model=self.model,
            input_type=input_type,
            embedding_types=["float"],
        )
        return res.embeddings.float_[0]
    
    async def embed_texts(self, texts: list[str]) -> list[float]:
        input_type = "search_document"
        res = self.cohere.embed(
            texts=texts,
            model=self.model,
            input_type=input_type,
            embedding_types=["float"],
        )
        return res.embeddings.float_
    