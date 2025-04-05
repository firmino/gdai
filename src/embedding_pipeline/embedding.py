from transformers import AutoModel




class EmbeddingModel:
    def __init__(self, model_name):
        self.model_name = model_name
    def embed_text(self, text:str) -> list[float]:
        pass
    def __str__(self):
        return self.model_name  


class JinaEmbeddingModel(EmbeddingModel):
    def __init__(self):
        model_name = "jinaai/jina-embeddings-v3"
        super().__init__(model_name) 
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)  
        
    def embed_text(self, texts:list[str]) -> list[list[float]]:
        embeddings = self.model.encode( texts, task="text-matching")
        return embeddings.tolist()        
