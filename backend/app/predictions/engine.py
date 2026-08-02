from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np

from ..memory.models import Memory, MemoryType, MemoryStatus

class PredictiveMemoryEngine:
    """Predict future states based on temporal patterns in memory."""

    def __init__(self):
        self.min_pattern_length = 2
        self.confidence_threshold = 0.6

    async def predict_next(self, db_session: AsyncSession, agent_id: Optional[str] = None,
                           context_query: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Predict what memory/state is most likely to follow given context."""
        stmt = select(Memory).where(Memory.status == MemoryStatus.ACTIVE)
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        stmt = stmt.order_by(Memory.created_at)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        if len(memories) < 3:
            return []

        # Find sequences where context_query appears
        if context_query:
            relevant_indices = [i for i, m in enumerate(memories) if context_query.lower() in m.content.lower()]
        else:
            relevant_indices = list(range(len(memories) - 1))

        # What typically follows these memories?
        next_memory_counts = defaultdict(lambda: {"count": 0, "memories": []})
        for idx in relevant_indices:
            if idx + 1 < len(memories):
                next_mem = memories[idx + 1]
                key = (next_mem.type.value, next_mem.content[:100])
                next_memory_counts[key]["count"] += 1
                next_memory_counts[key]["memories"].append(next_mem.id)
                next_memory_counts[key]["full_content"] = next_mem.content

        total = len(relevant_indices)
        predictions = []
        for key, data in sorted(next_memory_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:top_k]:
            confidence = min(0.95, data["count"] / total if total > 0 else 0)
            if confidence >= self.confidence_threshold:
                predictions.append({
                    "predicted_type": key[0],
                    "predicted_content": data["full_content"],
                    "confidence": round(confidence, 3),
                    "based_on_count": data["count"],
                    "sample_memory_ids": data["memories"][:3]
                })

        return predictions

    async def predict_trend(self, db_session: AsyncSession, entity: str,
                            agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Predict trend for an entity (increasing, decreasing, stable)."""
        stmt = select(Memory).where(
            Memory.status == MemoryStatus.ACTIVE,
            Memory.content.ilike(f"%{entity}%")
        )
        if agent_id:
            stmt = stmt.where(Memory.agent_id == agent_id)
        stmt = stmt.order_by(Memory.created_at)
        result = await db_session.execute(stmt)
        memories = result.scalars().all()

        if len(memories) < 3:
            return {"entity": entity, "trend": "insufficient_data", "confidence": 0.0}

        # Simple trend: check if confidence is increasing over time
        confidences = [m.confidence for m in memories]
        x = np.arange(len(confidences))
        slope = np.polyfit(x, confidences, 1)[0] if len(confidences) > 1 else 0

        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "entity": entity,
            "trend": trend,
            "slope": round(float(slope), 4),
            "confidence": round(min(0.95, abs(slope) * 10 + 0.3), 3),
            "data_points": len(memories),
            "latest_confidence": confidences[-1]
        }
