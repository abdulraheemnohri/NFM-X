""" Authorization implementation for NFM-X """

class Authorizer:
    def __init__(self, authenticator):
        self.authenticator = authenticator
    
    def check_permission(self, key, required_permission, resource=None):
        permissions = self.authenticator.get_permissions(key)
        return required_permission in permissions
    
    def check_scope(self, key, required_scope, resource=None):
        return True
    
    def get_allowed_actions(self, key, resource=None):
        return self.authenticator.get_permissions(key)