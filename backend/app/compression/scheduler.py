"""NFM-X V3 Compression Scheduler
Automatically compresses memories based on age and importance"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class CompressionConfig:
    """Configuration for automatic compression"""
    enabled: bool = True
    age_days: int = 30  # Compress memories older than this
    importance_threshold: float = 0.5  # Only compress memories with importance below this
    run_interval_hours: int = 24  # Run every 24 hours
    max_memories_per_run: int = 100  # Max memories to compress per run
    archive_enabled: bool = True  # Also archive old memories
    archive_age_days: int = 90  # Archive memories older than this
    
    @classmethod
    def from_env(cls) -> "CompressionConfig":
        """Load configuration from environment variables"""
        import os
        return cls(
            enabled=os.getenv("NFM_COMPRESSION_ENABLED", "true").lower() == "true",
            age_days=int(os.getenv("NFM_COMPRESSION_AGE_DAYS", "30")),
            importance_threshold=float(os.getenv("NFM_COMPRESSION_IMPORTANCE_THRESHOLD", "0.5")),
            run_interval_hours=int(os.getenv("NFM_COMPRESSION_RUN_INTERVAL_HOURS", "24")),
            max_memories_per_run=int(os.getenv("NFM_COMPRESSION_MAX_PER_RUN", "100")),
            archive_enabled=os.getenv("NFM_COMPRESSION_ARCHIVE_ENABLED", "true").lower() == "true",
            archive_age_days=int(os.getenv("NFM_COMPRESSION_ARCHIVE_AGE_DAYS", "90"))
        )


@dataclass
class CompressionRun:
    """Record of a compression run"""
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    memories_compressed: int = 0
    memories_archived: int = 0
    memories_skipped: int = 0
    total_bytes_saved: int = 0
    status: str = "running"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "memories_compressed": self.memories_compressed,
            "memories_archived": self.memories_archived,
            "memories_skipped": self.memories_skipped,
            "total_bytes_saved": self.total_bytes_saved,
            "status": self.status
        }
        if self.completed_at:
            result["completed_at"] = self.completed_at.isoformat()
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class MemoryCompressionResult:
    """Result of compressing a single memory"""
    memory_id: str
    compressed: bool
    archived: bool
    original_size: int
    compressed_size: int
    bytes_saved: int
    reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "compressed": self.compressed,
            "archived": self.archived,
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "bytes_saved": self.bytes_saved,
            "reason": self.reason
        }


class CompressionScheduler:
    """Schedules and runs automatic compression"""
    
    def __init__(self, config: Optional[CompressionConfig] = None):
        self.config = config or CompressionConfig()
        self.run_history: List[CompressionRun] = []
        self.current_run: Optional[CompressionRun] = None
        self._running = False
    
    async def start(self) -> None:
        """Start the compression scheduler"""
        if self._running:
            logger.warning("Compression scheduler already running")
            return
        
        self._running = True
        logger.info("Starting compression scheduler")
        
        while self._running:
            try:
                await self.run_compression()
            except Exception as e:
                logger.error(f"Error in compression scheduler: {str(e)}")
            
            # Wait for next interval
            await asyncio.sleep(self.config.run_interval_hours * 3600)
    
    async def stop(self) -> None:
        """Stop the compression scheduler"""
        self._running = False
        logger.info("Stopped compression scheduler")
    
    async def run_compression(self) -> Optional[CompressionRun]:
        """Run a single compression cycle"""
        if not self.config.enabled:
            logger.debug("Compression disabled, skipping run")
            return None
        
        run = CompressionRun(
            run_id=str(len(self.run_history)),
            started_at=datetime.utcnow(),
            status="running"
        )
        self.current_run = run
        
        try:
            logger.info(f"Starting compression run {run.run_id}")
            
            # Get memories eligible for compression
            memories = await self._get_eligible_memories()
            
            compressed_count = 0
            archived_count = 0
            skipped_count = 0
            total_saved = 0
            
            for memory in memories[:self.config.max_memories_per_run]:
                result = await self._compress_memory(memory)
                
                if result.compressed:
                    compressed_count += 1
                    total_saved += result.bytes_saved
                if result.archived:
                    archived_count += 1
                else:
                    skipped_count += 1
            
            run.memories_compressed = compressed_count
            run.memories_archived = archived_count
            run.memories_skipped = skipped_count
            run.total_bytes_saved = total_saved
            run.completed_at = datetime.utcnow()
            run.status = "completed"
            
            logger.info(f"Compression run {run.run_id} completed: {compressed_count} compressed, {archived_count} archived, {total_saved} bytes saved")
            
        except Exception as e:
            run.status = "failed"
            run.error = str(e)
            run.completed_at = datetime.utcnow()
            logger.error(f"Compression run {run.run_id} failed: {str(e)}")
        
        self.run_history.append(run)
        self.current_run = None
        return run
    
    async def _get_eligible_memories(self) -> List[Dict[str, Any]]:
        """Get memories eligible for compression"""
        # This would be implemented with actual database queries
        # For now, return an empty list as a placeholder
        return []
    
    async def _compress_memory(self, memory: Dict[str, Any]) -> MemoryCompressionResult:
        """Compress a single memory"""
        memory_id = memory.get("id", "unknown")
        importance = memory.get("importance", 0.0)
        created_at = memory.get("created_at")
        
        # Check if memory is eligible for compression
        if not self._is_eligible_for_compression(memory):
            return MemoryCompressionResult(
                memory_id=memory_id,
                compressed=False,
                archived=False,
                original_size=0,
                compressed_size=0,
                bytes_saved=0,
                reason="Not eligible for compression"
            )
        
        # Check if memory is eligible for archiving
        if self.config.archive_enabled and self._is_eligible_for_archive(memory):
            # Archive the memory
            return MemoryCompressionResult(
                memory_id=memory_id,
                compressed=False,
                archived=True,
                original_size=1000,  # Placeholder
                compressed_size=0,
                bytes_saved=1000,  # Placeholder
                reason="Archived due to age"
            )
        
        # Compress the memory
        return MemoryCompressionResult(
            memory_id=memory_id,
            compressed=True,
            archived=False,
            original_size=1000,  # Placeholder
            compressed_size=500,  # Placeholder
            bytes_saved=500,  # Placeholder
            reason="Compressed due to age and low importance"
        )
    
    def _is_eligible_for_compression(self, memory: Dict[str, Any]) -> bool:
        """Check if a memory is eligible for compression"""
        importance = memory.get("importance", 0.0)
        created_at_str = memory.get("created_at")
        
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age_days = (datetime.utcnow() - created_at).days
                if age_days < self.config.age_days:
                    return False
            except ValueError:
                pass
        
        if importance > self.config.importance_threshold:
            return False
        
        return True
    
    def _is_eligible_for_archive(self, memory: Dict[str, Any]) -> bool:
        """Check if a memory is eligible for archiving"""
        created_at_str = memory.get("created_at")
        
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age_days = (datetime.utcnow() - created_at).days
                if age_days < self.config.archive_age_days:
                    return False
            except ValueError:
                pass
        
        return True
    
    def get_config(self) -> CompressionConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> CompressionConfig:
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        return self.config
    
    def get_run_history(self, limit: int = 100) -> List[CompressionRun]:
        """Get history of compression runs"""
        return self.run_history[-limit:]
    
    def get_current_run(self) -> Optional[CompressionRun]:
        """Get the current running compression run"""
        return self.current_run