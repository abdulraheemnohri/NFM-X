"""Tests for NFM-X V2 Memory functionality"""

import pytest
from datetime import datetime
from backend.app.memory.v2.models_v2 import MemoryV2, MemoryModality, MemoryStatus


class TestMemoryV2:
    def test_memory_creation(self):
        """Test creating a V2 memory"""
        memory = MemoryV2(
            content="Test memory content",
            version=1,
            modality=MemoryModality.TEXT,
            status=MemoryStatus.ACTIVE
        )
        assert memory.content == "Test memory content"
        assert memory.version == 1
        assert memory.modality == MemoryModality.TEXT
    
    def test_memory_versioning(self):
        """Test memory version tracking"""
        memory_v1 = MemoryV2(
            id="mem_1",
            content="Version 1",
            version=1
        )
        memory_v2 = MemoryV2(
            id="mem_1",
            content="Version 2",
            version=2,
            previous_version_id="mem_1_v1"
        )
        assert memory_v2.version > memory_v1.version
        assert memory_v2.previous_version_id is not None
    
    def test_memory_modality(self):
        """Test different memory modalities"""
        for modality in [MemoryModality.TEXT, MemoryModality.IMAGE, MemoryModality.AUDIO]:
            memory = MemoryV2(content="test", modality=modality)
            assert memory.modality == modality