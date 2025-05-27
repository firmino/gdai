


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def embed(self, text: str) -> list[float]:
        # Placeholder for actual embedding logic
        return [0.0] * 768  # Example: returning a dummy embedding of size 768
    

class LLMModel:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        # Placeholder for actual LLM generation logic
        return f"Generated response for prompt: {prompt}"  # Example response