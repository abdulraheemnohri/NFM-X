"""NFM-X V3 Simulation Engine
Simulate scenarios with database persistence
"""

from typing import Dict, Any, List, Optional
from copy import deepcopy
from datetime import datetime, timezone
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete

from ..storage.database import AsyncSessionLocal
from .models import MemorySimulation, SimulatedMemory, SimulationActionLog, SimulationAction, SimulationStatus

logger = logging.getLogger(__name__)


class MemorySandbox:
    """Simulate scenarios with database persistence."""

    def __init__(self, memories: List[Dict[str, Any]], simulation_name: str = "default"):
        self.simulation_id = f"sim-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self.simulation_name = simulation_name
        self._session = None
        self._initialized = False
        self._original_memory_ids = [m.get('id', '') for m in memories if m.get('id')]
        
    async def initialize(self):
        """Initialize the simulation in the database"""
        if self._initialized:
            return
        
        session = AsyncSessionLocal()
        try:
            # Create simulation record
            simulation = MemorySimulation(
                id=str(uuid.uuid4()),
                simulation_id=self.simulation_id,
                name=self.simulation_name,
                description=f"Simulation created at {datetime.now(timezone.utc).isoformat()}",
                status=SimulationStatus.ACTIVE,
                original_memory_ids=self._original_memory_ids,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                metadata={"memory_count": len(self._original_memory_ids)}
            )
            
            session.add(simulation)
            await session.commit()
            await session.refresh(simulation)
            
            # Store original memories as simulated memories
            for mem in self._original_memory_ids:
                simulated_mem = SimulatedMemory(
                    id=str(uuid.uuid4()),
                    simulation_id=simulation.id,
                    memory_id=mem,
                    content="",  # Will be populated from original
                    is_injected=False,
                    is_modified=False,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(simulated_mem)
            
            await session.commit()
            self._session = session
            self._initialized = True
            logger.info(f"Initialized simulation: {self.simulation_id}")
            
        except Exception as e:
            await session.rollback()
            await session.close()
            logger.error(f"Failed to initialize simulation: {e}")
            raise
    
    async def close(self):
        """Close the database session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def inject_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Inject a hypothetical memory into the simulation with database persistence."""
        if not self._initialized:
            await self.initialize()
        
        session = self._session
        try:
            mem_copy = deepcopy(memory)
            mem_copy["id"] = f"sim_{mem_copy.get('id', str(uuid.uuid4()))}"
            mem_copy["_simulated"] = True
            
            # Create simulated memory record
            simulated_mem = SimulatedMemory(
                id=str(uuid.uuid4()),
                simulation_id=self._session.query(MemorySimulation).filter_by(simulation_id=self.simulation_id).first().id,
                memory_id=mem_copy["id"],
                content=mem_copy.get("content", ""),
                memory_type=mem_copy.get("type", "TEXT"),
                title=mem_copy.get("title"),
                source=mem_copy.get("source"),
                tags=mem_copy.get("tags", []),
                categories=mem_copy.get("categories", []),
                metadata=mem_copy.get("metadata", {}),
                is_injected=True,
                is_modified=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            session.add(simulated_mem)
            
            # Log the action
            action_log = SimulationActionLog(
                id=str(uuid.uuid4()),
                simulation_id=self._session.query(MemorySimulation).filter_by(simulation_id=self.simulation_id).first().id,
                action=SimulationAction.INJECT,
                memory_id=mem_copy["id"],
                details={"content_length": len(mem_copy.get("content", ""))},
                timestamp=datetime.now(timezone.utc)
            )
            session.add(action_log)
            
            await session.commit()
            await session.refresh(simulated_mem)
            
            logger.info(f"Injected memory: {mem_copy['id']} into simulation: {self.simulation_id}")
            return mem_copy
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to inject memory: {e}")
            raise
    
    async def remove_memory(self, memory_id: str) -> bool:
        """Remove a memory from the simulation with database persistence."""
        if not self._initialized:
            await self.initialize()
        
        session = self._session
        try:
            # Find and mark as removed in simulated memories
            result = await session.execute(
                select(SimulatedMemory)
                .where(SimulatedMemory.memory_id == memory_id)
                .where(SimulatedMemory.simulation_id == self._session.query(MemorySimulation).filter_by(simulation_id=self.simulation_id).first().id)
            )
            simulated_mem = result.scalar_one_or_none()
            
            if simulated_mem:
                # Mark as deleted instead of actually deleting (for history)
                simulated_mem.is_active = False
                simulated_mem.updated_at = datetime.now(timezone.utc)
                
                # Log the action
                action_log = SimulationActionLog(
                    id=str(uuid.uuid4()),
                    simulation_id=self._session.query(MemorySimulation).filter_by(simulation_id=self.simulation_id).first().id,
                    action=SimulationAction.REMOVE,
                    memory_id=memory_id,
                    details={"was_injected": simulated_mem.is_injected},
                    timestamp=datetime.now(timezone.utc)
                )
                session.add(action_log)
                
                await session.commit()
                logger.info(f"Removed memory: {memory_id} from simulation: {self.simulation_id}")
                return True
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to remove memory: {e}")
            return False
    
    async def modify_memory(self, memory_id: str, new_content: str) -> Optional[Dict[str, Any]]:
        """Modify a memory in the simulation with database persistence."""
        if not self._initialized:
            await self.initialize()
        
        session = self._session
        try:
            result = await session.execute(
                select(SimulatedMemory)
                .where(SimulatedMemory.memory_id == memory_id)
                .where(SimulatedMemory.simulation_id == self._session.query(MemorySimulation).filter_by(simulation_id=self.simulation_id).first().id)
            )
            simulated_mem = result.scalar_one_or_none()
            
            if simulated_mem:
                simulated_mem.content = new_content
                simulated_mem.is_modified = True
                simulated_mem.updated_at = datetime.now(timezone.utc)
                
                # Log the action
                action_log = SimulationActionLog(
                    id=str(uuid.uuid4()),
                    simulation_id=self._session.query(MemorySimulation).filter_by(simulation_id=self.simulation_id).first().id,
                    action=SimulationAction.MODIFY,
                    memory_id=memory_id,
                    details={"new_content_length": len(new_content)},
                    timestamp=datetime.now(timezone.utc)
                )
                session.add(action_log)
                
                await session.commit()
                await session.refresh(simulated_mem)
                
                logger.info(f"Modified memory: {memory_id} in simulation: {self.simulation_id}")
                return {
                    'id': simulated_mem.memory_id,
                    'content': simulated_mem.content,
                    '_modified': True
                }
            return None
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to modify memory: {e}")
            return None
    
    async def query_simulation(self, query: str) -> List[Dict[str, Any]]:
        """Search within simulated memories."""
        if not self._initialized:
            await self.initialize()
        
        session = self._session
        try:
            simulation = await session.get(MemorySimulation, self.simulation_id)
            if not simulation:
                return []
            
            result = await session.execute(
                select(SimulatedMemory)
                .where(SimulatedMemory.simulation_id == simulation.id)
                .where(SimulatedMemory.is_active == True)
            )
            simulated_mems = result.scalars().all()
            
            results = []
            query_lower = query.lower()
            for mem in simulated_mems:
                score = 0
                if query_lower in mem.content.lower():
                    score += 1.0
                if query_lower in mem.memory_type.lower():
                    score += 0.5
                if score > 0:
                    results.append({
                        'id': mem.memory_id,
                        'content': mem.content,
                        'type': mem.memory_type,
                        'title': mem.title,
                        'simulated_score': score,
                        '_simulated': mem.is_injected,
                        '_modified': mem.is_modified
                    })
            
            results.sort(key=lambda x: x["simulated_score"], reverse=True)
            
            # Log the query action
            action_log = SimulationActionLog(
                id=str(uuid.uuid4()),
                simulation_id=simulation.id,
                action=SimulationAction.QUERY,
                memory_id="",
                details={"query": query, "results_count": len(results)},
                timestamp=datetime.now(timezone.utc)
            )
            session.add(action_log)
            await session.commit()
            
            return results
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to query simulation: {e}")
            return []
    
    async def get_state(self) -> Dict[str, Any]:
        """Get the current state of the simulation from database."""
        if not self._initialized:
            await self.initialize()
        
        session = self._session
        try:
            simulation = await session.get(MemorySimulation, self.simulation_id)
            if not simulation:
                return {
                    "simulation_id": self.simulation_id,
                    "error": "Simulation not found"
                }
            
            # Count different types of memories
            result = await session.execute(
                select(SimulatedMemory)
                .where(SimulatedMemory.simulation_id == simulation.id)
            )
            all_mems = result.scalars().all()
            
            injected_count = sum(1 for m in all_mems if m.is_injected)
            modified_count = sum(1 for m in all_mems if m.is_modified)
            
            # Get action log
            result = await session.execute(
                select(SimulationActionLog)
                .where(SimulationActionLog.simulation_id == simulation.id)
                .order_by(SimulationActionLog.timestamp)
            )
            action_logs = result.scalars().all()
            
            return {
                "simulation_id": self.simulation_id,
                "name": simulation.name,
                "original_count": len(simulation.original_memory_ids or []),
                "simulated_count": len(all_mems),
                "injected_count": injected_count,
                "modified_count": modified_count,
                "status": simulation.status.value,
                "created_at": simulation.created_at.isoformat(),
                "log": [
                    {
                        "action": log.action.value,
                        "memory_id": log.memory_id,
                        "timestamp": log.timestamp.isoformat(),
                        "details": log.details
                    }
                    for log in action_logs
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get simulation state: {e}")
            return {
                "simulation_id": self.simulation_id,
                "error": str(e)
            }