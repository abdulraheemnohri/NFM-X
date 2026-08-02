from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid

class SharePermission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class MemoryBundle:
    """A portable package of memories for sharing between agents."""

    def __init__(self, source_agent_id: str, target_agent_id: str,
                 memories: List[Dict[str, Any]], permissions: SharePermission = SharePermission.READ):
        self.bundle_id = str(uuid.uuid4())
        self.source_agent_id = source_agent_id
        self.target_agent_id = target_agent_id
        self.memories = memories
        self.permissions = permissions
        self.created_at = datetime.now(timezone.utc)
        self.status = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "source_agent_id": self.source_agent_id,
            "target_agent_id": self.target_agent_id,
            "memory_count": len(self.memories),
            "permissions": self.permissions.value,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "memories": self.memories
        }

    def validate_bundle(self) -> bool:
        """Validate bundle integrity before import."""
        if not self.memories:
            return False
        for mem in self.memories:
            if not mem.get("content") or not mem.get("type"):
                return False
        return True
