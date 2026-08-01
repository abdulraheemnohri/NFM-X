""" Base provider class for NFM-X """

class BaseProvider:
    def __init__(self, config=None):
        self.config = config or {}
    
    def generate(self, prompt, context=None, max_tokens=512, temperature=0.7):
        raise NotImplementedError("Subclasses must implement generate method")
    
    def embed(self, text):
        raise NotImplementedError("Subclasses must implement embed method")
    
    def get_model_info(self):
        return {"model": "unknown", "type": "unknown"}
    
    def supports(self, feature):
        return False
    
    def initialize(self):
        return {"success": True}
    
    def cleanup(self):
        pass