"""NFM-X V3 Sync Conflict Auto-Resolution
Automatically resolves sync conflicts using configurable heuristics"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConflictResolutionStrategy(str, Enum):
    TIMESTAMP = "timestamp"        # Keep the most recent version
    VERSION = "version"           # Keep the highest version number
    MANUAL = "manual"            # Require manual resolution
    MERGE = "merge"              # Attempt to merge changes
    PREFER_SOURCE = "prefer_source"  # Prefer source device
    PREFER_SERVER = "prefer_server"  # Prefer server version



@dataclass
class SyncConflict:
    """Represents a synchronization conflict"""
    conflict_id: str
    memory_id: str
    local_version: str
    remote_version: str
    local_timestamp: datetime
    remote_timestamp: datetime
    local_content: Any
    remote_content: Any
    device_id: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolution_strategy: Optional[ConflictResolutionStrategy] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "memory_id": self.memory_id,
            "local_version": self.local_version,
            "remote_version": self.remote_version,
            "local_timestamp": self.local_timestamp.isoformat(),
            "remote_timestamp": self.remote_timestamp.isoformat(),
            "device_id": self.device_id,
            "detected_at": self.detected_at.isoformat(),
            "resolution_strategy": self.resolution_strategy.value if self.resolution_strategy else None,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes
        }


@dataclass
class ResolutionResult:
    """Result of a conflict resolution"""
    conflict_id: str
    success: bool
    resolution_strategy: ConflictResolutionStrategy
    resolved_content: Any
    notes: str
    resolved_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "success": self.success,
            "resolution_strategy": self.resolution_strategy.value,
            "resolved_content": self.resolved_content,
            "notes": self.notes,
            "resolved_at": self.resolved_at.isoformat()
        }


class SyncConflictResolver:
    """Automatically resolves synchronization conflicts"""
    
    def __init__(self, default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.TIMESTAMP):
        self.conflicts: Dict[str, SyncConflict] = {}
        self.resolution_history: List[ResolutionResult] = []
        self.default_strategy = default_strategy
        self.strategy_config: Dict[str, ConflictResolutionStrategy] = {}
    
    def detect_conflict(
        self,
        memory_id: str,
        local_version: str,
        remote_version: str,
        local_timestamp: datetime,
        remote_timestamp: datetime,
        local_content: Any,
        remote_content: Any,
        device_id: str
    ) -> SyncConflict:
        """
        Detect and register a synchronization conflict
        """
        conflict = SyncConflict(
            conflict_id=str(len(self.conflicts)),
            memory_id=memory_id,
            local_version=local_version,
            remote_version=remote_version,
            local_timestamp=local_timestamp,
            remote_timestamp=remote_timestamp,
            local_content=local_content,
            remote_content=remote_content,
            device_id=device_id
        )
        
        self.conflicts[conflict.conflict_id] = conflict
        logger.warning(f"Sync conflict detected: {memory_id} (versions: {local_version} vs {remote_version})")
        return conflict
    
    def auto_resolve(
        self,
        conflict_id: str,
        strategy: Optional[ConflictResolutionStrategy] = None
    ) -> ResolutionResult:
        """
        Automatically resolve a conflict using the specified strategy
        """
        conflict = self.conflicts.get(conflict_id)
        if not conflict:
            raise ValueError(f"Conflict {conflict_id} not found")
        
        if strategy is None:
            strategy = self.strategy_config.get(conflict.memory_id, self.default_strategy)
        
        conflict.resolution_strategy = strategy
        
        # Apply resolution strategy
        if strategy == ConflictResolutionStrategy.TIMESTAMP:
            resolved_content, notes = self._resolve_by_timestamp(conflict)
        elif strategy == ConflictResolutionStrategy.VERSION:
            resolved_content, notes = self._resolve_by_version(conflict)
        elif strategy == ConflictResolutionStrategy.MERGE:
            resolved_content, notes = self._resolve_by_merge(conflict)
        elif strategy == ConflictResolutionStrategy.PREFER_SOURCE:
            resolved_content, notes = self._resolve_prefer_source(conflict)
        elif strategy == ConflictResolutionStrategy.PREFER_SERVER:
            resolved_content, notes = self._resolve_prefer_server(conflict)
        else:
            resolved_content, notes = conflict.remote_content, "Manual resolution required"
        
        # Mark as resolved
        conflict.resolved = True
        conflict.resolved_at = datetime.utcnow()
        conflict.resolved_by = "auto-resolver"
        conflict.resolution_notes = notes
        
        # Record result
        result = ResolutionResult(
            conflict_id=conflict_id,
            success=True,
            resolution_strategy=strategy,
            resolved_content=resolved_content,
            notes=notes
        )
        
        self.resolution_history.append(result)
        logger.info(f"Auto-resolved conflict {conflict_id} using {strategy.value}")
        
        return result
    
    def auto_resolve_all(self, strategy: Optional[ConflictResolutionStrategy] = None) -> Dict[str, Any]:
        """
        Auto-resolve all unresolved conflicts
        """
        resolved = 0
        failed = 0
        results = []
        
        for conflict_id, conflict in self.conflicts.items():
            if not conflict.resolved:
                try:
                    result = self.auto_resolve(conflict_id, strategy)
                    resolved += 1
                    results.append(result.to_dict())
                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to resolve conflict {conflict_id}: {str(e)}")
        
        return {
            "resolved": resolved,
            "failed": failed,
            "results": results
        }
    
    def _resolve_by_timestamp(self, conflict: SyncConflict) -> Tuple[Any, str]:
        """Resolve by keeping the most recent version"""
        if conflict.local_timestamp > conflict.remote_timestamp:
            return conflict.local_content, "Resolved by timestamp: local is newer"
        else:
            return conflict.remote_content, "Resolved by timestamp: remote is newer"
    
    def _resolve_by_version(self, conflict: SyncConflict) -> Tuple[Any, str]:
        """Resolve by keeping the highest version number"""
        try:
            local_ver = int(conflict.local_version.replace("v", "").replace(".", ""))
            remote_ver = int(conflict.remote_version.replace("v", "").replace(".", ""))
            
            if local_ver > remote_ver:
                return conflict.local_content, "Resolved by version: local has higher version"
            else:
                return conflict.remote_content, "Resolved by version: remote has higher version"
        except ValueError:
            return conflict.remote_content, "Resolved by version: could not parse versions, prefer remote"
    
    def _resolve_by_merge(self, conflict: SyncConflict) -> Tuple[Any, str]:
        """Attempt to merge both versions"""
        # Simple merge: combine dictionaries
        if isinstance(conflict.local_content, dict) and isinstance(conflict.remote_content, dict):
            merged = {**conflict.remote_content, **conflict.local_content}
            return merged, "Resolved by merge: combined both versions"
        else:
            return conflict.remote_content, "Resolved by merge: could not merge, prefer remote"
    
    def _resolve_prefer_source(self, conflict: SyncConflict) -> Tuple[Any, str]:
        """Prefer the source (local) version"""
        return conflict.local_content, "Resolved by prefer_source: kept local version"
    
    def _resolve_prefer_server(self, conflict: SyncConflict) -> Tuple[Any, str]:
        """Prefer the server (remote) version"""
        return conflict.remote_content, "Resolved by prefer_server: kept remote version"
    
    def set_strategy_for_memory(self, memory_id: str, strategy: ConflictResolutionStrategy) -> None:
        """Set default strategy for a specific memory"""
        self.strategy_config[memory_id] = strategy
        logger.info(f"Set resolution strategy for {memory_id}: {strategy.value}")
    
    def list_conflicts(self, resolved: Optional[bool] = None) -> List[SyncConflict]:
        """List all conflicts, optionally filtered by resolution status"""
        if resolved is None:
            return list(self.conflicts.values())
        return [c for c in self.conflicts.values() if c.resolved == resolved]
    
    def get_resolution_history(self, limit: int = 100) -> List[ResolutionResult]:
        """Get resolution history"""
        return self.resolution_history[-limit:]