""" Transformers provider for NFM-X """

class TransformersProvider:
    def __init__(self, model_name="distilbert-base-uncased", device="cpu"):
        self.model_name = model_name
        self.device = device
    
    def generate(self, prompt, context=None, max_tokens=512):
        return {"text": "Response from Transformers", "model": self.model_name}
    
    def embed(self, text):
        return [0.0] * 768
    
    def load_model(self):
        return {"loaded": True, "model": self.model_name}