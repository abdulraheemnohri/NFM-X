""" Ollama provider for NFM-X """

class OllamaProvider:
    def __init__(self, base_url="http://localhost:11434", model="llama3"):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt, context=None, max_tokens=512):
        return {"text": "Response from Ollama", "model": self.model}
    
    def list_models(self):
        return [self.model]
    
    def pull_model(self, model_name):
        return {"success": True, "model": model_name}