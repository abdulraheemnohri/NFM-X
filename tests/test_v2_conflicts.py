"""Tests for NFM-X V2 Conflicts functionality"""

import pytest
from backend.app.conflicts.v2.auto_resolver import ConflictAutoResolver, Conflict, ConflictType, ConflictSeverity, ConflictStatus


class TestConflictsV2:
    def test_conflict_creation(self):
        """Test creating a conflict"""
        conflict = Conflict(
            conflict_id="conflict_1",
            memory_ids=["mem_1", "mem_2"],
            conflict_type=ConflictType.CONTENT_DUPLICATE,
            severity=ConflictSeverity.MEDIUM
        )
        assert conflict.conflict_id == "conflict_1"
        assert len(conflict.memory_ids) == 2
    
    def test_conflict_resolver_init(self):
        """Test conflict resolver initialization"""
        resolver = ConflictAutoResolver()
        assert hasattr(resolver, "conflicts")
        assert hasattr(resolver, "detect_conflicts")
        assert hasattr(resolver, "auto_resolve")
    
    def test_auto_resolve_all(self):
        """Test auto-resolving all conflicts"""
        resolver = ConflictAutoResolver()
        resolved, failed = resolver.auto_resolve_all()
        assert isinstance(resolved, int)
        assert isinstance(failed, int)