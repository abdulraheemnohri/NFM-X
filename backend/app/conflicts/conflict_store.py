"""
Conflict storage implementation for NFM-X
"""

class ConflictStore:
    """
    Stores and manages conflicts.
    """
    
    def __init__(self):
        self.conflicts = {}
    
    def store_conflict(self, conflict_id, memory_ids, conflict_type, status="unresolved"):
        """
        Store a new conflict.
        
        Args:
            conflict_id: Unique identifier for the conflict
            memory_ids: List of conflicting memory IDs
            conflict_type: Type of conflict
            status: Initial status
            
        Returns:
            Conflict object
        """
        self.conflicts[conflict_id] = {
            "id": conflict_id,
            "memory_ids": memory_ids,
            "type": conflict_type,
            "status": status,
            "detected_at": "2026-08-01T00:00:00Z",
            "resolved_at": None,
            "resolution": None
        }
        return self.conflicts[conflict_id]
    
    def get_conflict(self, conflict_id):
        """
        Get conflict by ID.
        
        Args:
            conflict_id: ID of the conflict
            
        Returns:
            Conflict object or None
        """
        return self.conflicts.get(conflict_id)
    
    def update_conflict(self, conflict_id, updates):
        """
        Update a conflict.
        
        Args:
            conflict_id: ID of the conflict
            updates: Dictionary with updates
            
        Returns:
            Updated conflict object
        """
        if conflict_id in self.conflicts:
            self.conflicts[conflict_id].update(updates)
        return self.conflicts.get(conflict_id)
    
    def list_conflicts(self, status=None):
        """
        List all conflicts, optionally filtered by status.
        
        Args:
            status: Filter by status (unresolved, resolved, dismissed)
            
        Returns:
            List of conflict objects
        """
        if status:
            return [c for c in self.conflicts.values() if c["status"] == status]
        return list(self.conflicts.values())