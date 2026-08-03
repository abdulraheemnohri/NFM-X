"""
NFM-X V4 API Tests
Tests for V4 specific features.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


# ==================== V4 HEALTH CHECK TESTS ====================

class TestV4Health:
    """Tests for V4 health check endpoints."""
    
    def test_detailed_health(self):
        """Test detailed health check."""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "subsystems" in data
        assert "timestamp" in data
    
    def test_subsystems_health(self):
        """Test individual subsystem health."""
        response = client.get("/api/health/subsystems")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "database" in data
        assert "vector_store" in data
    
    def test_health_uptime(self):
        """Test uptime endpoint."""
        response = client.get("/api/health/uptime")
        assert response.status_code == 200
        data = response.json()
        assert "uptime" in data


# ==================== V4 OCR TESTS ====================

class TestV4OCR:
    """Tests for V4 OCR features."""
    
    def test_ocr_process(self):
        """Test OCR processing."""
        response = client.post(
            "/api/ocr/process",
            files={"file": ("test.pdf", b"Test PDF content")},
            data={"language": "eng"}
        )
        assert response.status_code in [200, 202]
    
    def test_ocr_async_job(self):
        """Test async OCR job creation."""
        response = client.post(
            "/api/ocr/async",
            json={"document_id": "test_doc", "language": "eng"}
        )
        assert response.status_code in [200, 202]
        data = response.json()
        assert "job_id" in data
    
    def test_ocr_table_extraction(self):
        """Test table extraction from documents."""
        response = client.post(
            "/api/ocr/tables",
            files={"file": ("test.pdf", b"Test PDF with tables")}
        )
        assert response.status_code in [200, 202]


# ==================== V4 DOCUMENTS TESTS ====================

class TestV4Documents:
    """Tests for V4 document management."""
    
    def test_create_document(self):
        """Test creating a document record."""
        response = client.post(
            "/api/documents",
            json={
                "name": "test.pdf",
                "type": "pdf",
                "size": 1024,
                "pages": 5
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    def test_get_document(self):
        """Test getting a document."""
        # First create
        create_response = client.post(
            "/api/documents",
            json={"name": "test2.pdf", "type": "pdf"}
        )
        doc_id = create_response.json()["id"]
        
        # Then get
        response = client.get(f"/api/documents/{doc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id


# ==================== V4 BATCH TESTS ====================

class TestV4Batch:
    """Tests for batch upload."""
    
    def test_batch_upload(self):
        """Test batch upload of multiple files."""
        response = client.post(
            "/api/batch/upload",
            files=[
                ("files", ("file1.pdf", b"Content 1")),
                ("files", ("file2.pdf", b"Content 2")),
            ]
        )
        assert response.status_code in [200, 202]
        data = response.json()
        assert "job_id" in data


# ==================== V4 CONFLICTS TESTS ====================

class TestV4Conflicts:
    """Tests for V4 conflict resolution."""
    
    def test_create_conflict(self):
        """Test creating a conflict record."""
        response = client.post(
            "/api/conflicts",
            json={
                "memory_id": "mem_123",
                "local_content": "Local version",
                "remote_content": "Remote version",
                "conflict_type": "content"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    def test_resolve_conflict(self):
        """Test resolving a conflict."""
        # First create
        create_response = client.post(
            "/api/conflicts",
            json={
                "memory_id": "mem_456",
                "local_content": "Local",
                "remote_content": "Remote",
                "conflict_type": "content"
            }
        )
        conflict_id = create_response.json()["id"]
        
        # Then resolve
        response = client.post(
            f"/api/conflicts/{conflict_id}/resolve",
            json={"resolution": "keep_both"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
    
    def test_auto_resolve_conflicts(self):
        """Test auto-resolving conflicts."""
        response = client.post(
            "/api/conflicts/auto-resolve",
            json={"strategy": "keep_local", "dry_run": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_conflicts" in data


# ==================== V4 PATTERNS TESTS ====================

class TestV4Patterns:
    """Tests for V4 pattern search."""
    
    def test_search_with_pattern(self):
        """Test searching with a regex pattern."""
        response = client.post(
            "/api/patterns/search",
            json={
                "pattern": r"d+",
                "case_sensitive": False,
                "limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_with_saved_pattern(self):
        """Test searching with a saved pattern."""
        # First create a pattern
        create_response = client.post(
            "/api/patterns",
            json={
                "name": "Number Pattern",
                "pattern": r"d+",
                "description": "Matches numbers"
            }
        )
        pattern_id = create_response.json()["id"]
        
        # Then search with it
        response = client.post(f"/api/patterns/{pattern_id}/search")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ==================== V4 SKILLS TESTS ====================

class TestV4Skills:
    """Tests for V4 skill execution."""
    
    def test_create_skill(self):
        """Test creating a skill."""
        response = client.post(
            "/api/skills",
            json={
                "name": "Test Skill",
                "description": "A test skill",
                "skill_type": "extraction",
                "handler": "skills.test_handler",
                "version": "1.0.0"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
    
    def test_execute_skill(self):
        """Test executing a skill."""
        # First create
        create_response = client.post(
            "/api/skills",
            json={
                "name": "Executor Skill",
                "description": "Test execution",
                "skill_type": "custom",
                "handler": "skills.dummy_handler"
            }
        )
        skill_id = create_response.json()["id"]
        
        # Then execute
        response = client.post(
            f"/api/skills/{skill_id}/execute",
            json={"input_data": {"test": "value"}}
        )
        assert response.status_code in [200, 202]
        data = response.json()
        assert "execution_id" in data


# ==================== V4 MCP TESTS ====================

class TestV4MCP:
    """Tests for V4 MCP authentication."""
    
    def test_create_api_key(self):
        """Test creating an API key."""
        response = client.post(
            "/api/mcp/keys",
            json={
                "name": "Test API Key",
                "description": "For testing",
                "permissions": ["read", "write"],
                "rate_limit": 100
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "secret" in data
    
    def test_authenticate_api_key(self):
        """Test authenticating with an API key."""
        # First create
        create_response = client.post(
            "/api/mcp/keys",
            json={"name": "Auth Test Key", "permissions": ["read"]}
        )
        api_key = create_response.json()["secret"]
        
        # Then authenticate
        response = client.post(
            "/api/mcp/authenticate",
            json={"api_key": api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
    
    def test_rate_limit_info(self):
        """Test getting rate limit information."""
        response = client.get(
            "/api/mcp/rate-limit",
            headers={"X-API-Key": "test_key"}
        )
        assert response.status_code in [200, 401]  # 401 if invalid key


# Run tests
if __name__ == "__main__":
    pytest.main(["-v", "-x", __file__])
