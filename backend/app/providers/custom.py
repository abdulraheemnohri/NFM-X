""" Custom provider for NFM-X """

class CustomProvider:
    def __init__(self, config):
        self.config = config
    
    def generate(self, prompt, context=None, max_tokens=512):
        return {"text": "Response from custom provider", "model": "custom"}
    
    def initialize(self):
        return {"success": True}
    
    def cleanup(self):
        pass