""" Integrity checking implementation for NFM-X """

import hashlib

class IntegrityChecker:
    def __init__(self):
        self.hash_chain = []
    
    def calculate_hash(self, data):
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    def add_to_chain(self, data):
        data_hash = self.calculate_hash(data)
        if self.hash_chain:
            combined = data_hash + self.hash_chain[-1]
        else:
            combined = data_hash
        self.hash_chain.append(self.calculate_hash(combined))
        return self.hash_chain[-1]
    
    def verify_chain(self):
        if len(self.hash_chain) <= 1:
            return True
        for i in range(1, len(self.hash_chain)):
            if self.hash_chain[i] != self.hash_chain[i-1]:
                return False
        return True
    
    def verify_data(self, data, expected_hash):
        return self.calculate_hash(data) == expected_hash
    
    def create_checkpoint(self):
        return {"hash": self.hash_chain[-1] if self.hash_chain else None, "count": len(self.hash_chain)}