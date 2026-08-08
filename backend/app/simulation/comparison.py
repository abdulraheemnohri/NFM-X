"""NFM-X V3 Simulation Comparison
Compares simulated memory states with real memory states"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryState:
    """Represents the state of a memory at a point in time"""
    memory_id: str
    content: Any
    version: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags
        }


@dataclass
class SimulationState:
    """Represents a simulated state of the memory system"""
    simulation_id: str
    name: str
    description: str
    created_at: datetime
    memories: Dict[str, MemoryState] = field(default_factory=dict)  # memory_id -> MemoryState
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_memory_state(self, state: MemoryState) -> None:
        """Add a memory state to the simulation"""
        self.memories[state.memory_id] = state
    
    def get_memory_state(self, memory_id: str) -> Optional[MemoryState]:
        """Get a memory state from the simulation"""
        return self.memories.get(memory_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "memory_count": len(self.memories),
            "memories": {mid: s.to_dict() for mid, s in self.memories.items()},
            "metadata": self.metadata
        }


@dataclass
class MemoryDiff:
    """Represents differences between two memory states"""
    memory_id: str
    diff_type: str  # "added", "removed", "modified"
    simulated_state: Optional[MemoryState] = None
    real_state: Optional[MemoryState] = None
    changes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "memory_id": self.memory_id,
            "diff_type": self.diff_type,
            "changes": self.changes
        }
        if self.simulated_state:
            result["simulated_state"] = self.simulated_state.to_dict()
        if self.real_state:
            result["real_state"] = self.real_state.to_dict()
        return result


@dataclass
class SimulationDiff:
    """Complete diff between simulation and real state"""
    simulation_id: str
    compared_at: datetime
    added: List[MemoryDiff] = field(default_factory=list)
    removed: List[MemoryDiff] = field(default_factory=list)
    modified: List[MemoryDiff] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "compared_at": self.compared_at.isoformat(),
            "summary": self.summary,
            "added": [d.to_dict() for d in self.added],
            "removed": [d.to_dict() for d in self.removed],
            "modified": [d.to_dict() for d in self.modified]
        }


class SimulationComparator:
    """Compares simulated states with real states"""
    
    def __init__(self):
        self.simulations: Dict[str, SimulationState] = {}
        self.real_states: Dict[str, MemoryState] = {}  # Current real memory states
        self.diff_history: List[SimulationDiff] = []
    
    def create_simulation(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> SimulationState:
        """Create a new simulation state"""
        simulation = SimulationState(
            simulation_id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        self.simulations[simulation.simulation_id] = simulation
        logger.info(f"Created simulation: {simulation.simulation_id}")
        return simulation
    
    def get_simulation(self, simulation_id: str) -> Optional[SimulationState]:
        """Get a simulation by ID"""
        return self.simulations.get(simulation_id)
    
    def update_real_state(self, memory_id: str, state: MemoryState) -> None:
        """Update the real state of a memory"""
        self.real_states[memory_id] = state
        logger.debug(f"Updated real state for {memory_id}")
    
    def compare_simulation(self, simulation_id: str) -> SimulationDiff:
        """
        Compare a simulation with the current real state
        
        Returns a diff showing added, removed, and modified memories
        """
        simulation = self.simulations.get(simulation_id)
        if not simulation:
            raise ValueError(f"Simulation {simulation_id} not found")
        
        added = []
        removed = []
        modified = []
        
        # Find memories in simulation but not in real state
        sim_memory_ids = set(simulation.memories.keys())
        real_memory_ids = set(self.real_states.keys())
        
        # Added: in simulation but not in real
        for mem_id in sim_memory_ids - real_memory_ids:
            added.append(MemoryDiff(
                memory_id=mem_id,
                diff_type="added",
                simulated_state=simulation.memories[mem_id]
            ))
        
        # Removed: in real but not in simulation
        for mem_id in real_memory_ids - sim_memory_ids:
            removed.append(MemoryDiff(
                memory_id=mem_id,
                diff_type="removed",
                real_state=self.real_states[mem_id]
            ))

        
        # Modified: in both but different
        for mem_id in sim_memory_ids & real_memory_ids:
            sim_state = simulation.memories[mem_id]
            real_state = self.real_states[mem_id]
            
            if self._states_differ(sim_state, real_state):
                changes = self._calculate_changes(sim_state, real_state)
                modified.append(MemoryDiff(
                    memory_id=mem_id,
                    diff_type="modified",
                    simulated_state=sim_state,
                    real_state=real_state,
                    changes=changes
                ))
        
        # Create diff result
        diff = SimulationDiff(
            simulation_id=simulation_id,
            compared_at=datetime.now(timezone.utc),
            added=added,
            removed=removed,
            modified=modified,
            summary={
                "total_added": len(added),
                "total_removed": len(removed),
                "total_modified": len(modified),
                "total_simulated": len(sim_memory_ids),
                "total_real": len(real_memory_ids)
            }
        )
        
        self.diff_history.append(diff)
        logger.info(f"Compared simulation {simulation_id}: {len(added)} added, {len(removed)} removed, {len(modified)} modified")
        
        return diff
    
    def _states_differ(self, state1: MemoryState, state2: MemoryState) -> bool:
        """Check if two memory states differ"""
        # Compare content, version, and metadata
        if state1.content != state2.content:
            return True
        if state1.version != state2.version:
            return True
        if state1.metadata != state2.metadata:
            return True
        if set(state1.tags) != set(state2.tags):
            return True
        return False
    
    def _calculate_changes(self, sim_state: MemoryState, real_state: MemoryState) -> Dict[str, Any]:
        """Calculate specific changes between two
 states"""
        changes = {}
        
        if sim_state.content != real_state.content:
            changes["content"] = {
                "simulated": str(sim_state.content)[:100],
                "real": str(real_state.content)[:100]
            }
        
        if sim_state.version != real_state.version:
            changes["version"] = {
                "simulated": sim_state.version,
                "real": real_state.version
            }
        
        if sim_state.metadata != real_state.metadata:
            changes["metadata"] = {
                "added": {k: v for k, v in sim_state.metadata.items() if k not in real_state.metadata},
                "removed": {k: v for k, v in real_state.metadata.items() if k not in sim_state.metadata},
                "modified": {
                    k: {"simulated": sim_state.metadata[k], "real": real_state.metadata[k]}
                    for k in set(sim_state.metadata.keys()) & set(real_state.metadata.keys())
                    if sim_state.metadata[k] != real_state.metadata[k]
                }
            }
        
        if set(sim_state.tags) != set(real_state.tags):
            changes["tags"] = {
                "added": list(set(sim_state.tags) - set(real_state.tags)),
                "removed": list(set(real_state.tags) - set(sim_state.tags))
            }
        
        return changes
    
    def list_simulations(self) -> List[Dict[str, Any]]:
        """List all simulations"""
        return [
            {
                "simulation_id": s.simulation_id,
                "name": s.name,
                "description": s.description,
                "created_at": s.created_at.isoformat(),
                "memory_count": len(s.memories)
            }
            for s in self.simulations.values()
        ]
    
    def get_diff_history(self, limit: int = 100) -> List[SimulationDiff]:
        """Get history of simulation comparisons"""
        return self.diff_history[-limit:]