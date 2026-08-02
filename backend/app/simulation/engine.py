from typing import Dict, Any, List, Optional
from copy import deepcopy
from datetime import datetime, timezone

class MemorySandbox:
    """Simulate scenarios without affecting real memory."""

    def __init__(self, memories: List[Dict[str, Any]]):
        self.original_memories = memories
        self.simulated_memories = deepcopy(memories)
        self.simulation_log = []
        self.simulation_id = f"sim-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    def inject_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Inject a hypothetical memory into the simulation."""
        mem_copy = deepcopy(memory)
        mem_copy["id"] = f"sim_{mem_copy.get('id', 'new')}"
        mem_copy["_simulated"] = True
        self.simulated_memories.append(mem_copy)
        self.simulation_log.append({"action": "inject", "memory_id": mem_copy["id"]})
        return mem_copy

    def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the simulation."""
        original_count = len(self.simulated_memories)
        self.simulated_memories = [m for m in self.simulated_memories if m.get("id") != memory_id]
        removed = len(self.simulated_memories) < original_count
        if removed:
            self.simulation_log.append({"action": "remove", "memory_id": memory_id})
        return removed

    def modify_memory(self, memory_id: str, new_content: str) -> Optional[Dict[str, Any]]:
        """Modify a memory in the simulation."""
        for mem in self.simulated_memories:
            if mem.get("id") == memory_id:
                mem["content"] = new_content
                mem["_modified"] = True
                self.simulation_log.append({"action": "modify", "memory_id": memory_id})
                return mem
        return None

    def query_simulation(self, query: str) -> List[Dict[str, Any]]:
        """Search within simulated memories."""
        results = []
        query_lower = query.lower()
        for mem in self.simulated_memories:
            score = 0
            if query_lower in mem.get("content", "").lower():
                score += 1.0
            if query_lower in mem.get("type", "").lower():
                score += 0.5
            if score > 0:
                results.append({**mem, "simulated_score": score})
        results.sort(key=lambda x: x["simulated_score"], reverse=True)
        return results

    def get_state(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "original_count": len(self.original_memories),
            "simulated_count": len(self.simulated_memories),
            "injected_count": sum(1 for m in self.simulated_memories if m.get("_simulated")),
            "modified_count": sum(1 for m in self.simulated_memories if m.get("_modified")),
            "log": self.simulation_log
        }
