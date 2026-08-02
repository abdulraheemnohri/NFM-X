import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class IntegrityChain:
    def __init__(self):
        self.algorithm = "sha256"

    def hash_memory(self, memory_data: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
        """Create a cryptographic hash of memory data including previous hash."""
        data = {
            "memory": {k: str(v) if v is not None else None for k, v in memory_data.items()},
            "previous_hash": previous_hash or "0" * 64,
            "timestamp": memory_data.get("created_at") or "1970-01-01T00:00:00Z"
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def verify_chain(self, memories: list) -> bool:
        """Verify that a sequence of memories forms a valid integrity chain."""
        for i, mem in enumerate(memories):
            expected_prev = memories[i - 1]["integrity_hash"] if i > 0 else "0" * 64
            recalculated = self.hash_memory(mem, expected_prev)
            if recalculated != mem.get("integrity_hash"):
                return False
        return True
