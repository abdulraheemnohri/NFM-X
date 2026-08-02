from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from ..memory.models import Memory, MemoryRelationship, MemoryType, MemoryStatus

class CausalExtractionEngine:
    CAUSAL_PATTERNS = [
        (r"(\w+(?:\s+\w+){0,5})\s+caused?\s+(\w+(?:\s+\w+){0,10})", "caused"),
        (r"(\w+(?:\s+\w+){0,5})\s+led?\s+to\s+(\w+(?:\s+\w+){0,10})", "led_to"),
        (r"(\w+(?:\s+\w+){0,5})\s+resulted?\s+in\s+(\w+(?:\s+\w+){0,10})", "resulted_in"),
        (r"because\s+(\w+(?:\s+\w+){0,10})\s*,?\s+(\w+(?:\s+\w+){0,10})", "because"),
        (r"if\s+(\w+(?:\s+\w+){0,10})\s*,?\s+then\s+(\w+(?:\s+\w+){0,10})", "if_then"),
        (r"(\w+(?:\s+\w+){0,5})\s+increased?\s+(\w+(?:\s+\w+){0,10})", "increased"),
        (r"(\w+(?:\s+\w+){0,5})\s+decreased?\s+(\w+(?:\s+\w+){0,10})", "decreased"),
    ]

    def extract_causal_relationships(self, content: str) -> List[Dict[str, str]]:
        relationships = []
        for pattern, rel_type in self.CAUSAL_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                cause, effect = match.group(1).strip(), match.group(2).strip()
                if len(cause) > 3 and len(effect) > 3:
                    relationships.append({"cause": cause, "effect": effect,
                                          "relationship_type": rel_type, "source_text": match.group(0)})
        return relationships

    async def store_causal_memory(self, db_session: AsyncSession, source_memory_id: str, cause: str, effect: str, relationship_type: str):
        content = f"Cause: {cause}. Effect: {effect}. Relationship: {relationship_type}"
        mem = Memory(
            id=str(uuid.uuid4()), root_id=str(uuid.uuid4()), version=1,
            type=MemoryType.CAUSAL, content=content, normalized_content=content.lower(),
            source_id=source_memory_id, confidence=0.6, importance=0.7,
            status=MemoryStatus.ACTIVE, created_at=datetime.now(timezone.utc),
            observed_at=datetime.now(timezone.utc), valid_from=datetime.now(timezone.utc),
            metadata={"cause": cause, "effect": effect, "relationship_type": relationship_type,
                      "source_memory_id": source_memory_id, "verified": False}
        )
        db_session.add(mem)
        rel = MemoryRelationship(id=str(uuid.uuid4()), memory_id=source_memory_id, related_id=mem.id,
            relationship_type="causes", confidence=0.6)
        db_session.add(rel)
        await db_session.commit()
        return mem
