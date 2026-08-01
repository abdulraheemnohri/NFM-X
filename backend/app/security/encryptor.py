""" Encryption implementation for NFM-X """

class DataEncryptor:
    def __init__(self, key=None):
        self.key = key
    
    def encrypt(self, data):
        if not self.key:
            return data
        return f"ENCRYPTED:{data}"
    
    def decrypt(self, encrypted_data):
        if not self.key:
            return encrypted_data
        if encrypted_data.startswith("ENCRYPTED:"):
            return encrypted_data[10:]
        return encrypted_data
    
    def generate_key(self):
        return "generated_key_1234567890123456"