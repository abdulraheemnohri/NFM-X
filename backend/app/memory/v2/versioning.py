"""NFM-X V2 Versioning System - Complete memory version history management"""

from typing import List, Optional, Dict
from datetime import datetime
from .models_v2 import MemoryV2, MemoryVersion


class MemoryVersionManager:
    """Manages version history and rollback for memories"""
    
    def __init__(self):
        self.versions: Dict[str, List[MemoryVersion]] = {}
    
    def add_version(self, memory_id: str, content: str, metadata: Dict, changes: Dict) -> MemoryVersion:
        """Add a new version to memory history"""
        existing_versions = self.versions.get(memory_id, [])
        version_number = len(existing_versions) + 1
        
        version = MemoryVersion(
            version_id=f"{memory_id}_v{version_number}",
            memory_id=memory_id,
            content=content,
            version_number=version_number,
            created_at=datetime.now(),
            metadata=metadata,
            changes=changes
        )
        
        self.versions.setdefault(memory_id, []).append(version)
        return version
    
    def get_versions(self, memory_id: str) -> List[MemoryVersion]:
        """Get all versions of a memory"""
        return self.versions.get(memory_id, [])
    
    def rollback(self, memory_id: str, version_number: int) -> Optional[MemoryVersion]:
        """Rollback to a specific version"""
        versions = self.versions.get(memory_id, [])
        for v in versions:
            if v.version_number == version_number:
                return v
        return None
    
    def get_latest(self, memory_id: str) -> Optional[MemoryVersion]:
        """Get the latest version of a memory"""
        versions = self.versions.get(memory_id, [])
        return versions[-1] if versions else None