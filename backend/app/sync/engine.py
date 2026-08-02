from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryStatus, MemoryType, MemoryVersion

class SyncEngine:
    """Synchronize memories across devices."""

    async def generate_sync_payload(self, db_session: AsyncSession, device_id: str,
                                     last_sync: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate sync payload for a device."""
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if last_sync:
            stmt = stmt.where(Memory.created_at > last_sync)
        stmt = stmt.order_by(Memory.created_at)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        return {
            "device_id": device_id,
            "sync_timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_count": len(memories),
            "memories": [
                {
                    "id": m.id, "root_id": m.root_id, "version": m.version,
                    "type": m.type.value, "content": m.content,
                    "confidence": m.confidence, "importance": m.importance,
                    "status": m.status.value, "created_at": m.created_at.isoformat(),
                    "agent_id": m.agent_id, "metadata": m.metadata
                }
                for m in memories
            ]
        }

    async def apply_sync_payload(self, db_session: AsyncSession, payload: Dict[str, Any],
                                  local_device_id: str) -> Dict[str, Any]:
        """Apply incoming sync payload. Detect and report conflicts."""
        conflicts = []
        imported = []
        skipped = []

        for mem_data in payload.get("memories", []):
            # Check if memory already exists locally
            result = await db_session.execute(select(Memory).where(Memory.id == mem_data["id"]))
            existing = result.scalar_one_or_none()

            if existing:
                # Conflict detection: same ID, different content
                if existing.content != mem_data["content"]:
                    if existing.created_at > datetime.fromisoformat(mem_data["created_at"].replace("Z", "+00:00")):
                        # Local is newer — keep local, report conflict
                        conflicts.append({
                            "memory_id": mem_data["id"],
                            "resolution": "local_wins",
                            "local_version": existing.version,
                            "remote_version": mem_data["version"],
                            "reason": "Local memory is newer"
                        })
                        skipped.append(mem_data["id"])
                    else:
                        # Remote is newer — create new version
                        from ..memory.evolution import MemoryEvolution
                        evo = MemoryEvolution()
                        new_version = await evo.create_version(
                            db_session=db_session,
                            memory_id=existing.id,
                            new_content=mem_data["content"],
                            change_type="sync_update" if hasattr(ChangeType, 'sync_update') else ChangeType.REFINE,
                            change_reason=f"Synced from device {payload.get('device_id', 'unknown')}",
                            actor_id="sync",
                            confidence=mem_data.get("confidence", existing.confidence)
                        )
                        imported.append(new_version.id)
                        conflicts.append({
                            "memory_id": mem_data["id"],
                            "resolution": "remote_wins",
                            "new_version_id": new_version.id,
                            "reason": "Remote memory is newer"
                        })
                else:
                    # Same content — no conflict
                    skipped.append(mem_data["id"])
            else:
                # New memory — import directly
                new_mem = Memory(
                    id=mem_data["id"],
                    root_id=mem_data.get("root_id", mem_data["id"]),
                    version=mem_data.get("version", 1),
                    type=MemoryType(mem_data["type"]),
                    content=mem_data["content"],
                    normalized_content=mem_data["content"].lower().strip(),
                    agent_id=mem_data.get("agent_id"),
                    source_id=f"sync:{payload.get('device_id', 'unknown')}",
                    confidence=mem_data.get("confidence", 0.7),
                    importance=mem_data.get("importance", 0.5),
                    status=MemoryStatus.ACTIVE,
                    created_at=datetime.fromisoformat(mem_data["created_at"].replace("Z", "+00:00")),
                    observed_at=datetime.now(timezone.utc),
                    valid_from=datetime.now(timezone.utc),
                    metadata={
                        **(mem_data.get("metadata") or {}),
                        "synced_from": payload.get("device_id"),
                        "synced_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                db_session.add(new_mem)
                imported.append(new_mem.id)

        await db_session.commit()
        return {
            "imported": imported,
            "skipped": skipped,
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "local_device_id": local_device_id
        }
