from transformers import AutoModel, AutoTokenizer




class EmbeddingModel:
    def __init__(self, model_name):
        self.model_name = model_name
    def embed_text(self, text:str) -> list[float]:
        pass
    def __str__(self):
        return self.model_name  


class MistralEmbeddingModel(EmbeddingModel):
    def __init__(self):
        model_name = "mistralai/Mistral-7B-v0.1"
        super().__init__("mistral")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name, device_map="auto")  
        
    def embed_text(self, text:str) -> list[float]:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        return embeddings        
