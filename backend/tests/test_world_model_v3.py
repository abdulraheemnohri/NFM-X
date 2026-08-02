"""Tests for NFM-X V3 World Model features"""

import pytest
from datetime import datetime
from backend.app.world_model.merge import WorldModelMerger, Entity, MergeStrategy, MergeResult


class TestWorldModelV3:
    def test_entity_creation(self):
        """Test creating an entity"""
        merger = WorldModelMerger()
        entity = Entity(
            entity_id="entity_1",
            name="Test Entity",
            entity_type="concept",
            attributes={"color": "blue", "size": "large"}
        )
        merger.add_entity(entity)
        
        retrieved = merger.get_entity("entity_1")
        assert retrieved is not None
        assert retrieved.name == "Test Entity"
        assert retrieved.entity_type == "concept"
    
    def test_entity_merge_combine(self):
        """Test merging entities with COMBINE strategy"""
        merger = WorldModelMerger()
        
        entity1 = Entity(
            entity_id="entity_1",
            name="Entity 1",
            entity_type="concept",
            attributes={"color": "blue"}
        )
        entity2 = Entity(
            entity_id="entity_2",
            name="Entity 2",
            entity_type="concept",
            attributes={"size": "large"}
        )
        
        merger.add_entity(entity1)
        merger.add_entity(entity2)
        
        result = merger.merge_entities("entity_1", "entity_2", MergeStrategy.COMBINE)
        
        assert result.success is True
        assert result.merged_entity_id == "entity_2"
        assert "color" in result.attributes_merged
        assert "size" in result.attributes_merged
    
    def test_entity_merge_prefer_source(self):
        """Test merging entities with PREFER_SOURCE strategy"""
        merger = WorldModelMerger()
        
        entity1 = Entity(            entity_id="entity_1",
            name="Entity 1",
            entity_type="concept",
            attributes={"color": "blue"}
        )
        entity2 = Entity(
            entity_id="entity_2",
            name="Entity 2",
            entity_type="concept",
            attributes={"color": "red"}
        )
        
        merger.add_entity(entity1)
        merger.add_entity(entity2)
        
        result = merger.merge_entities("entity_1", "entity_2", MergeStrategy.PREFER_SOURCE)
        
        assert result.success is True
        assert result.attributes_merged["color"] == "blue"
    
    def test_entity_merge_prefer_target(self):
        """Test merging entities with PREFER_TARGET strategy"""
        merger = WorldModelMerger()
        
        entity1 = Entity(
            entity_id="entity_1",
            name="Entity 1",
            entity_type="concept",
            attributes={"color": "blue"}
        )
        entity2 = Entity(
            entity_id="entity_2",
            name="Entity 2",
            entity_type="concept",
            attributes={"color": "red"}
        )
        
        merger.add_entity(entity1)
        merger.add_entity(entity2)
        
        result = merger.merge_entities("entity_1", "entity_2", MergeStrategy.PREFER_TARGET)
        
        assert result.success is True
        assert result.attributes_merged["color"] == "red"
    
    def test_merge_history(self):
        """Test merge history tracking"""
        merger = WorldModelMerger()
        
        entity1 = Entity(entity_id="entity_1", name="Entity 1")
        entity2 = Entity(entity_id="entity_2", name="Entity 2")
        
        merger.add_entity(entity1)
        merger.add_entity(entity2)
        merger.merge_entities("entity_1", "entity_2")
        
        history = merger.get_merge_history()
        assert len(history) == 1
        assert history[0].success is True
    
    def test_list_entities(self):
        """Test listing entities"""
        merger = WorldModelMerger()
        
        merger.add_entity(Entity(entity_id="entity_1", name="Entity 1", entity_type="person"))
        merger.add_entity(Entity(entity_id="entity_2", name="Entity 2", entity_type="location"))
        merger.add_entity(Entity(entity_id="entity_3", name="Entity 3", entity_type="person"))
        
        all_entities = merger.list_entities()
        assert len(all_entities) == 3
        
        people = merger.list_entities("person")
        assert len(people) == 2
        
        locations = merger.list_entities("location")
        assert len(locations) == 1