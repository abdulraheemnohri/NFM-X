"""
Source tracking implementation for NFM-X
"""

class SourceTracker:
    """
    Tracks sources of information.
    """
    
    def __init__(self):
        self.sources = {}
    
    def add_source(self, source_id, source_type, reference, reliability=1.0):
        """
        Add a new source.
        
        Args:
            source_id: Unique identifier for the source
            source_type: Type of source (user, document, api, etc.)
            reference: Reference to the source (URL, path, etc.)
            reliability: Reliability score (0.0 to 1.0)
            
        Returns:
            Source object
        """
        self.sources[source_id] = {
            "id": source_id,
            "type": source_type,
            "reference": reference,
            "reliability": reliability,
            "created_at": "2026-08-01T00:00:00Z"
        }
        return self.sources[source_id]
    
    def get_source(self, source_id):
        """
        Get source by ID.
        
        Args:
            source_id: ID of the source
            
        Returns:
            Source object or None
        """
        return self.sources.get(source_id)
    
    def update_reliability(self, source_id, reliability):
        """
        Update reliability score for a source.
        
        Args:
            source_id: ID of the source
            reliability: New reliability score
            
        Returns:
            Updated source object
        """
        if source_id in self.sources:
            self.sources[source_id]["reliability"] = reliability
        return self.sources.get(source_id)