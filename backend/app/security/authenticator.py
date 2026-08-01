""" Authentication implementation for NFM-X """

class Authenticator:
    def __init__(self):
        self.api_keys = {}
    
    def add_api_key(self, key, name, permissions=None):
        self.api_keys[key] = {
            "key": key, "name": name, "permissions": permissions or []
        }
        return self.api_keys[key]
    
    def validate_api_key(self, key):
        return key in self.api_keys
    
    def get_permissions(self, key):
        return self.api_keys.get(key, {}).get("permissions", [])
    
    def remove_api_key(self, key):
        if key in self.api_keys:
            del self.api_keys[key]
        return True