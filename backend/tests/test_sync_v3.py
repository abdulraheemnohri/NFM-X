"""Tests for NFM-X V3 Sync Conflict Resolution"""

import pytest
from datetime import datetime
from backend.app.sync.auto_resolve import SyncConflictResolver, ConflictResolutionStrategy, SyncConflict


class TestSyncV3:
    def test_detect_conflict(self):
        """Test detecting a sync conflict"""
        resolver = SyncConflictResolver()
        
        now = datetime.utcnow()
        conflict = resolver.detect_conflict(
            memory_id="mem_1",
            local_version="v1",
            remote_version="v2",
            local_timestamp=now,
            remote_timestamp=now,
            local_content={"text": "local"},
            remote_content={"text": "remote"},
            device_id="device_1"
        )
        
        assert conflict.conflict_id == "0"
        assert conflict.memory_id == "mem_1"
        assert conflict.resolved is False
    
    def test_auto_resolve_timestamp(self):
        """Test auto-resolving by timestamp"""
        resolver = SyncConflictResolver(default_strategy=ConflictResolutionStrategy.TIMESTAMP)
        
        now = datetime.utcnow()
        past = now - timedelta(days=1)
        
        resolver.detect_conflict(
            memory_id="mem_1",
            local_version="v1",
            remote_version="v2",
            local_timestamp=now,
            remote_timestamp=past,
            local_content={"text": "local"},
            remote_content={"text": "remote"},
            device_id="device_1"
        )
        
        result = resolver.auto_resolve("0")
        assert result.success is True
        assert result.resolution_strategy == ConflictResolutionStrategy.TIMESTAMP
        assert result.resolved_content == {"text": "local"}
    
    def test_auto_resolve_version(self):
        """Test auto-resolving by version"""
        resolver = SyncConflictResolver(default_strategy=ConflictResolutionStrategy.VERSION)
        
        now = datetime.utcnow()
        resolver.detect_conflict(
            memory_id="mem_1",
            local_version="v2",
            remote_version="v1",
            local_timestamp=now,
            remote_timestamp=now,
            local_content={"text": "local"},
            remote_content={"text": "remote"},
            device_id="device_1"
        )
        
        result = resolver.auto_resolve("0")
        assert result.success is True
        assert result.resolution_strategy == ConflictResolutionStrategy.VERSION
        assert result.resolved_content == {"text": "local"}
    
    def test_auto_resolve_merge(self):
        """Test auto-resolving by merge"""
        resolver = SyncConflictResolver(default_strategy=ConflictResolutionStrategy.MERGE)
        
        now = datetime.utcnow()
        resolver.detect_conflict(
            memory_id="mem_1",
            local_version="v1",
            remote_version="v2",
            local_timestamp=now,
            remote_timestamp=now,
            local_content={"text": "local", "color": "blue"},
            remote_content={"text": "remote", "size": "large"},
            device_id="device_1"
        )
        
        result = resolver.auto_resolve("0")
        assert result.success is True
        assert "text" in result.resolved_content
        assert "color" in result.resolved_content
        assert "size" in result.resolved_content
    
    def test_auto_resolve_all(self):
        """Test auto-resolving all conflicts"""
        resolver = SyncConflictResolver()
        
        now = datetime.utcnow()
        resolver.detect_conflict("mem_1", "v1", "v2", now, now, {"text": "a"}, {"text": "b"}, "device_1")
        resolver.detect_conflict("mem_2", "v1", "v2", now, now, {"text": "c"}, {"text": "d"}, "device_1")
        
        result = resolver.auto_resolve_all()
        assert result["resolved"] == 2
        assert result["failed"] == 0
    
    def test_set_strategy_for_memory(self):
        """Test setting strategy for specific memory"""
        resolver = SyncConflictResolver()
        resolver.set_strategy_for_memory("mem_1", ConflictResolutionStrategy.PREFER_SOURCE)
        
        assert resolver.strategy_config["mem_1"] == ConflictResolutionStrategy.PREFER_SOURCE
    
    def test_list_conflicts(self):
        """Test listing conflicts"""
        resolver = SyncConflictResolver()
        
        now = datetime.utcnow()
        resolver.detect_conflict("mem_1", "v1", "v2", now, now, {}, {}, "device_1")
        resolver.detect_conflict("mem_2", "v1", "v2", now, now, {}, {}, "device_1")
        
        conflicts = resolver.list_conflicts(resolved=False)
        assert len(conflicts) == 2
    
    def test_nonexistent_conflict(self):
        """Test resolving non-existent conflict"""
        resolver = SyncConflictResolver()
        
        with pytest.raises(ValueError):
            resolver.auto_resolve("999")