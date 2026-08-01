""" OpenAI-compatible provider for NFM-X """

class OpenAICompatibleProvider:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
    
    def generate(self, prompt, context=None, max_tokens=512):
        return {"text": "Response from OpenAI-compatible API", "model": "unknown"}
    
    def get_models(self):
        return []
    
    def check_health(self):
        return {"healthy": True}