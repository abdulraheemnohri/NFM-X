"""NFM-X V3 Simulation API
Simulation state management and comparison"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.app.simulation.comparison import SimulationComparator, SimulationState, MemoryState

router = APIRouter(prefix="/api/v1/simulation", tags=["Simulation"])


class MemoryStateRequest(BaseModel):
    memory_id: str
    content: Dict[str, Any]
    version: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class CreateSimulationRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None


class SimulationResponse(BaseModel):
    simulation_id: str
    name: str
    description: str
    created_at: datetime
    memory_count: int
    metadata: Dict[str, Any]


class MemoryDiffResponse(BaseModel):
    memory_id: str
    diff_type: str
    changes: Dict[str, Any]
    simulated_state: Optional[Dict[str, Any]] = None
    real_state: Optional[Dict[str, Any]] = None


class SimulationDiffResponse(BaseModel):
    simulation_id: str
    compared_at: datetime
    summary: Dict[str, int]
    added: List[MemoryDiffResponse]
    removed: List[MemoryDiffResponse]
    modified: List[MemoryDiffResponse]


# Initialize comparator
simulation_comparator = SimulationComparator()


@router.post("/", response_model=SimulationResponse, status_code=201)
async def create_simulation(request: CreateSimulationRequest):
    """
    Create a new simulation state
    """
    simulation = simulation_comparator.create_simulation(
        name=request.name,
        description=request.description or "",
        metadata=request.metadata or {}
    )
    
    return SimulationResponse(
        simulation_id=simulation.simulation_id,
        name=simulation.name,
        description=simulation.description,
        created_at=simulation.created_at,
        memory_count=len(simulation.memories),
        metadata=simulation.metadata
    )


@router.get("/", response_model=List[SimulationResponse])
async def list_simulations():
    """
    List all simulations
    """
    simulations = simulation_comparator.list_simulations()
    return [
        SimulationResponse(
            simulation_id=s["simulation_id"],
            name=s["name"],
            description=s["description"],
            created_at=datetime.fromisoformat(s["created_at"]),
            memory_count=s["memory_count"],
            metadata=s["metadata"]
        )
        for s in simulations
    ]


@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: str):
    """
    Get a specific simulation
    """
    simulation = simulation_comparator.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail=f"Simulation {simulation_id} not found")
    
    return SimulationResponse(
        simulation_id=simulation.simulation_id,
        name=simulation.name,
        description=simulation.description,
        created_at=simulation.created_at,
        memory_count=len(simulation.memories),
        metadata=simulation.metadata
    )


@router.post("/{simulation_id}/memories", status_code=201)
async def add_simulation_memory(simulation_id: str, state: MemoryStateRequest):
    """
    Add a memory state to a simulation
    """
    simulation = simulation_comparator.get_simulation(simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail=f"Simulation {simulation_id} not found")
    
    memory_state = MemoryState(
        memory_id=state.memory_id,
        content=state.content,
        version=state.version,
        timestamp=state.timestamp,
        metadata=state.metadata or {},
        tags=state.tags or []
    )
    
    simulation.add_memory_state(memory_state)
    return {"message": f"Added memory {state.memory_id} to simulation {simulation_id}"}


@router.get("/{simulation_id}/diff", response_model=SimulationDiffResponse)
async def compare_simulation(simulation_id: str):
    """
    Compare a simulation with the current real state
    
    Returns differences showing what was added, removed, or modified
    """
    try:
        diff = simulation_comparator.compare_simulation(simulation_id)
        
        return SimulationDiffResponse(
            simulation_id=diff.simulation_id,
            compared_at=diff.compared_at,
            summary=diff.summary,
            added=[
                MemoryDiffResponse(
                    memory_id=d.memory_id,
                    diff_type=d.diff_type,
                    changes=d.changes,
                    simulated_state=d.simulated_state.to_dict() if d.simulated_state else None,
                    real_state=d.real_state.to_dict() if d.real_state else None
                )
                for d in diff.added
            ],
            removed=[
                MemoryDiffResponse(
                    memory_id=d.memory_id,
                    diff_type=d.diff_type,
                    changes=d.changes,
                    simulated_state=d.simulated_state.to_dict() if d.simulated_state else None,
                    real_state=d.real_state.to_dict() if d.real_state else None
                )
                for d in diff.removed
            ],
            modified=[
                MemoryDiffResponse(
                    memory_id=d.memory_id,
                    diff_type=d.diff_type,
                    changes=d.changes,
                    simulated_state=d.simulated_state.to_dict() if d.simulated_state else None,
                    real_state=d.real_state.to_dict() if d.real_state else None
                )
                for d in diff.modified
            ]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{simulation_id}/update-real", status_code=200)
async def update_real_state(simulation_id: str, state: MemoryStateRequest):
    """
    Update the real state of a memory (for comparison)
    """
    memory_state = MemoryState(
        memory_id=state.memory_id,
        content=state.content,
        version=state.version,
        timestamp=state.timestamp,
        metadata=state.metadata or {},
        tags=state.tags or []
    )
    
    simulation_comparator.update_real_state(state.memory_id, memory_state)
    return {"message": f"Updated real state for memory {state.memory_id}"}