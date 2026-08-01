""" Text handling implementation for NFM-X """

class TextHandler:
    def __init__(self):
        pass
    
    def process_text(self, text, metadata=None):
        return {"type": "text", "content": text, "metadata": metadata or {}}
    
    def extract_entities(self, text):
        return []
    
    def normalize_text(self, text):
        return text.lower().strip()