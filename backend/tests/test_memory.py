""" Tests for memory module """

class TestMemoryModels:
    def test_memory_creation(self):
        from backend.app.memory.models import MemoryCreate
        memory_data = MemoryCreate(
            type="semantic",
            content="Test",
            agent_id="agent-001"
        )
        assert memory_data.type == "semantic"
        return True