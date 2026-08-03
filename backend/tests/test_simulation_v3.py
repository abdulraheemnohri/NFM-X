"""Tests for NFM-X V3 Simulation Comparison"""

import pytest
from datetime import datetime, timedelta
from backend.app.simulation.comparison import SimulationComparator, SimulationState, MemoryState, SimulationDiff


class TestSimulationV3:
    def test_create_simulation(self):
        """Test creating a simulation"""
        comparator = SimulationComparator()
        simulation = comparator.create_simulation("Test Simulation", "Description")
        
        assert simulation.simulation_id is not None
        assert simulation.name == "Test Simulation"
        assert simulation.description == "Description"
    
    def test_add_memory_state(self):
        """Test adding memory states to simulation"""
        comparator = SimulationComparator()
        simulation = comparator.create_simulation("Test Simulation")
        
        state = MemoryState(
            memory_id="mem_1",
            content={"text": "test"},
            version="v1",
            timestamp=datetime.now(timezone.utc)(),
            metadata={"importance": 0.5}
        )
        simulation.add_memory_state(state)
        
        assert len(simulation.memories) == 1
        assert "mem_1" in simulation.memories
    
    def test_compare_simulation(self):
        """Test comparing simulation with real state"""
        comparator = SimulationComparator()
        simulation = comparator.create_simulation("Test Simulation")
        
        # Add states to simulation
        sim_state = MemoryState(
            memory_id="mem_1",
            content={"text": "simulated"},
            version="v2",
            timestamp=datetime.now(timezone.utc)()
        )
        simulation.add_memory_state(sim_state)
        
        # Add real state
        real_state = MemoryState(
            memory_id="mem_1",
            content={"text": "real"},
            version="v1",
            timestamp=datetime.now(timezone.utc)()
        )
        comparator.update_real_state("mem_1", real_state)
        
        # Compare
        diff = compar
ator.compare_simulation(simulation.simulation_id)
        
        assert len(diff.modified) == 1
        assert diff.modified[0].memory_id == "mem_1"
        assert diff.modified[0].diff_type == "modified"
    
    def test_compare_added_memories(self):
        """Test detecting added memories in simulation"""
        comparator = SimulationComparator()
        simulation = comparator.create_simulation("Test Simulation")
        
        # Add state only in simulation
        sim_state = MemoryState(
            memory_id="mem_1",
            content={"text": "new"},
            version="v1",
            timestamp=datetime.now(timezone.utc)()
        )
        simulation.add_memory_state(sim_state)
        
        # Compare with empty real state
        diff = comparator.compare_simulation(simulation.simulation_id)
        
        assert len(diff.added) == 1
        assert diff.added[0].memory_id == "mem_1"
    
    def test_compare_removed_memories(self):
        """Test detecting removed memories"""
        comparator = SimulationComparator()
        simulation = comparator.create_simulation("Test Simulation")
        
        # Add state to real but not simulation
        real_state = MemoryState(
            memory_id="mem_1",
            content={"text": "real only"},
            version="v1",
            timestamp=datetime.now(timezone.utc)()
        )
        comparator.update_real_state("mem_1", real_state)
        
        # Compare with empty simulation
        diff = comparator.compare_simulation(simulation.simulation_id)
        
        assert len(diff.removed) == 1
        assert diff.removed[0].memory_id == "mem_1"
    
    def test_list_simulations(self):
        """Test listing simulations"""
        comparator = SimulationComparator()
        comparator.create_simulation("Simulation 1")
        comparator.create_simulation("Simulation 2")
        
        simulations = comparator.list_simulations()
        assert len(simulations) == 2
    
    def test_get_simulation
(self):
        """Test getting a specific simulation"""
        comparator = SimulationComparator()
        simulation = comparator.create_simulation("Test Simulation")
        
        retrieved = comparator.get_simulation(simulation.simulation_id)
        assert retrieved is not None
        assert retrieved.simulation_id == simulation.simulation_id
    
    def test_get_nonexistent_simulation(self):
        """Test getting non-existent simulation"""
        comparator = SimulationComparator()
        
        retrieved = comparator.get_simulation("nonexistent")
        assert retrieved is None
    
    def test_states_differ(self):
        """Test state difference detection"""
        comparator = SimulationComparator()
        
        state1 = MemoryState("mem_1", {"text": "a"}, "v1", datetime.now(timezone.utc)())
        state2 = MemoryState("mem_1", {"text": "b"}, "v1", datetime.now(timezone.utc)())
        
        assert comparator._states_differ(state1, state2) is True
        
        state3 = MemoryState("mem_1", {"text": "a"}, "v1", datetime.now(timezone.utc)())
        assert comparator._states_differ(state1, state3) is False