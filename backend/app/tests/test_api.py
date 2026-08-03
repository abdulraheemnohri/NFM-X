"""
NFM-X API Tests
Comprehensive test suite for all API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database import Base, get_db, engine
from backend.app.config import NFM_DATABASE_URL

# Test client
client = TestClient(app)


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async def override_get_db():
        AsyncTestingSessionLocal = sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        async with AsyncTestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield
    
    # Cleanup
    app.dependency_overrides.clear()


# ==================== HEALTH CHECK TESTS ====================

class TestHealthCheck:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test simple health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_detailed_health_endpoint(self):
        """Test detailed health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "subsystems" in data


# ==================== MEMORY API TESTS ====================

class TestMemoryAPI:
    """Tests for memory CRUD operations."""
    
    def test_create_memory(self):
        """Test creating a new memory."""
        response = client.post(
            "/api/v1/memories",
            json={
                "content": "Test memory content",
                "subtype": "text",
                "metadata": {"source": "test"}
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["content"] == "Test memory content"
    
    def test_list_memories(self):
        """Test listing all memories."""
        response = client.get("/api/v1/memories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_memory(self):
        """Test getting a specific memory."""
        # First create a memory
        create_response = client.post(
            "/api/v1/memories",
            json={"content": "Test memory for get"}
        )
        memory_id = create_response.json()["id"]
        
        # Then get it
        response = client.get(f"/api/v1/memories/{memory_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == memory_id
    
    def test_update_memory(self):
        """Test updating a memory."""
        # Create
        create_response = client.post(
            "/api/v1/memories",
            json={"content": "Original content"}
        )
        memory_id = create_response.json()["id"]
        
        # Update
        response = client.put(
            f"/api/v1/memories/{memory_id}",
            json={"content": "Updated content"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"
    
    def test_delete_memory(self):
        """Test deleting a memory."""
        # Create
        create_response = client.post(
            "/api/v1/memories",
            json={"content": "Memory to delete"}
        )
        memory_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/api/v1/memories/{memory_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/memories/{memory_id}")
        assert get_response.status_code == 404


# ==================== SEARCH API TESTS ====================

class TestSearchAPI:
    """Tests for search functionality."""
    
    def test_search_memories(self):
        """Test searching memories."""
        # First create some memories
        client.post("/api/v1/memories", json={"content": "Test content one"})
        client.post("/api/v1/memories", json={"content": "Test content two"})
        
        response = client.get("/api/v1/search?q=Test")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ==================== OCR API TESTS ====================

class TestOCRAPI:
    """Tests for OCR processing."""
    
    def test_ocr_health(self):
        """Test OCR service health."""
        response = client.get("/api/ocr/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_ocr_config(self):
        """Test OCR configuration."""
        response = client.get("/api/ocr/config")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "backends" in data


# ==================== DOCUMENTS API TESTS ====================

class TestDocumentsAPI:
    """Tests for document management."""
    
    def test_list_documents(self):
        """Test listing documents."""
        response = client.get("/api/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_upload_document(self):
        """Test uploading a document."""
        response = client.post(
            "/api/documents",
            files={"file": ("test.txt", b"Test content")},
            data={"name": "test.txt"}
        )
        assert response.status_code in [200, 201]


# ==================== PATTERNS API TESTS ====================

class TestPatternsAPI:
    """Tests for pattern search."""
    
    def test_list_patterns(self):
        """Test listing patterns."""
        response = client.get("/api/patterns")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_pattern(self):
        """Test creating a pattern."""
        response = client.post(
            "/api/patterns",
            json={
                "name": "Email Pattern",
                "pattern": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Z|a-z]{2,}",
                "description": "Matches email addresses"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Email Pattern"
    
    def test_validate_pattern(self):
        """Test pattern validation."""
        # Valid pattern
        response = client.post(
            "/api/patterns/validate",
            json={"pattern": r"d+"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        
        # Invalid pattern
        response = client.post(
            "/api/patterns/validate",
            json={"pattern": "[invalid"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


# ==================== SKILLS API TESTS ====================

class TestSkillsAPI:
    """Tests for skill execution."""
    
    def test_list_skills(self):
        """Test listing skills."""
        response = client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_executions(self):
        """Test listing skill executions."""
        response = client.get("/api/skills/executions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ==================== MCP API TESTS ====================

class TestMCPAPI:
    """Tests for MCP authentication."""
    
    def test_mcp_config(self):
        """Test MCP configuration."""
        response = client.get("/api/mcp/config")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "require_authentication" in data
    
    def test_list_api_keys(self):
        """Test listing API keys."""
        response = client.get("/api/mcp/keys")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ==================== CONFLICTS API TESTS ====================

class TestConflictsAPI:
    """Tests for conflict resolution."""
    
    def test_list_conflicts(self):
        """Test listing conflicts."""
        response = client.get("/api/conflicts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ==================== COMPRESSION API TESTS ====================

class TestCompressionAPI:
    """Tests for compression scheduler."""
    
    def test_compression_config(self):
        """Test compression configuration."""
        response = client.get("/api/v3/compression")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data


# ==================== STATS API TESTS ====================

class TestStatsAPI:
    """Tests for statistics."""
    
    def test_get_stats(self):
        """Test getting statistics."""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_memories" in data


# ==================== ERROR HANDLING TESTS ====================

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_not_found(self):
        """Test 404 for non-existent resource."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test 405 for invalid HTTP method."""
        response = client.post("/api/health")
        assert response.status_code == 405


# Run tests
if __name__ == "__main__":
    pytest.main(["-v", "-x", __file__])
