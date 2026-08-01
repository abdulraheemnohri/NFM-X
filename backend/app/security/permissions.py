""" Permission management implementation """

class PermissionManager:
    PERMISSIONS = ["READ", "WRITE", "EVOLVE", "CONFIRM", "EXPORT", "ADMIN"]
    SCOPES = ["PRIVATE", "AGENT", "PROJECT", "TEAM", "SHARED", "SYSTEM"]
    
    def __init__(self):
        self.permissions = {}
    
    def grant_permission(self, user_id, permission, resource=None):
        key = (user_id, resource) if resource else user_id
        if key not in self.permissions:
            self.permissions[key] = set()
        self.permissions[key].add(permission)
        return True
    
    def revoke_permission(self, user_id, permission, resource=None):
        key = (user_id, resource) if resource else user_id
        if key in self.permissions and permission in self.permissions[key]:
            self.permissions[key].remove(permission)
        return True
    
    def check_permission(self, user_id, permission, resource=None):
        key = (user_id, resource) if resource else user_id
        return key in self.permissions and permission in self.permissions[key]
    
    def get_permissions(self, user_id, resource=None):
        key = (user_id, resource) if resource else user_id
        return list(self.permissions.get(key, set()))