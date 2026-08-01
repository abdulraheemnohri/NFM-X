""" Audit logging implementation for NFM-X """

import datetime

class AuditLogger:
    def __init__(self):
        self.logs = []
    
    def log_action(self, action, user, resource=None, success=True, details=None):
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "action": action,
            "user": user,
            "resource": resource,
            "success": success,
            "details": details or {}
        }
        self.logs.append(log_entry)
        return log_entry
    
    def get_logs(self, filters=None, limit=100):
        if filters:
            return [l for l in self.logs if self.match_filters(l, filters)][:limit]
        return self.logs[-limit:]
    
    def match_filters(self, log, filters):
        for key, value in filters.items():
            if log.get(key) != value:
                return False
        return True
    
    def export_logs(self, format="json"):
        if format == "json":
            return self.logs
        return str(self.logs)