"""Tests for NFM-X V2 Graph functionality"""

import pytest
from backend.app.graph.v2.relationships import MemoryRelationshipManager, RelationshipType, MemoryRelationship


class TestGraphV2:
    def test_add_relationship(self):
        """Test adding a relationship between memories"""
        manager = MemoryRelationshipManager()
        rel = manager.add_relationship(
            source_id="mem_1",
            target_id="mem_2",
            relationship_type=RelationshipType.CAUSAL,
            weight=0.8
        )
        assert rel.source_id == "mem_1"
        assert rel.target_id == "mem_2"
        assert rel.relationship_type == RelationshipType.CAUSAL
    
    def test_get_relationships(self):
        """Test retrieving relationships for a memory"""
        manager = MemoryRelationshipManager()
        manager.add_relationship("mem_1", "mem_2", RelationshipType.SEMANTIC)
        manager.add_relationship("mem_1", "mem_3", RelationshipType.TEMPORAL)
        
        relationships = manager.get_relationships("mem_1")
        assert len(relationships) == 2
    
    def test_bidirectional_connections(self):
        """Test that relationships are bidirectional"""
        manager = MemoryRelationshipManager()
        manager.add_relationship("mem_1", "mem_2", RelationshipType.CAUSAL)
        
        connected = manager.get_connected_memories("mem_1")
        assert "mem_2" in connected
        
        connected_reverse = manager.get_connected_memories("mem_2")
        assert "mem_1" in connected_reverse