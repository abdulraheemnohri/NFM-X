""" Local LLM provider for NFM-X """

class LocalLLMProvider:
    def __init__(self, model_path, config=None):
        self.model_path = model_path
        self.config = config or {}
    
    def generate(self, prompt, context=None, max_tokens=512):
        return {"text": "Response from local LLM", "model": self.model_path}
    
    def get_model_info(self):
        return {"model": self.model_path, "type": "local"}
    
    def supports(self, feature):
        return feature in ["text-generation", "embeddings"]