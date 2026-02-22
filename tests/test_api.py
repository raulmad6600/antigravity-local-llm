"""
Test suite for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from api.main import app
from api.deps import reset_singletons
from core.models import Task, AgentContext, AgentResult


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    reset_singletons()
    return TestClient(app)


@pytest.fixture
async def mock_orchestrator():
    """Create a mock orchestrator for testing."""
    orchestrator = AsyncMock()
    orchestrator.run = AsyncMock(return_value={
        "plan": "Test plan",
        "implementation": "Test implementation",
        "review": "Test review - PASS"
    })
    return orchestrator


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "app" in data
    assert "debug" in data


def test_v1_query_endpoint(client):
    """Test the /v1/query endpoint returns 200."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={
            "plan": "Test plan",
            "implementation": "Test code",
            "review": "Test review"
        })
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/query", json={
            "prompt": "Write a hello world function"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
        assert "id" in data


def test_v1_chat_completions_returns_valid_structure(client):
    """Test that /v1/chat/completions returns valid OpenAI-compatible structure."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={
            "plan": "Test plan",
            "implementation": "def hello(): return 'world'",
            "review": "PASS - Code looks good"
        })
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/chat/completions", json={
            "model": "local",
            "messages": [
                {"role": "user", "content": "Write a hello world function"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify OpenAI-compatible structure
        assert data["object"] == "chat.completion"
        assert "id" in data
        assert data["id"].startswith("chatcmpl-")
        assert "created" in data
        assert "model" in data
        assert data["model"] == "local"
        assert "choices" in data
        assert len(data["choices"]) > 0
        
        choice = data["choices"][0]
        assert choice["index"] == 0
        assert "message" in choice
        assert choice["message"]["role"] == "assistant"
        assert "content" in choice["message"]
        assert choice["finish_reason"] == "stop"


def test_chat_completions_with_multiple_messages(client):
    """Test chat completion with multiple messages."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={
            "implementation": "Generated response"
        })
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/chat/completions", json={
            "model": "local",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "Help me code"}
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["choices"]) > 0


def test_chat_completions_no_user_message(client):
    """Test chat completion fails when no user message is provided."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/chat/completions", json={
            "model": "local",
            "messages": [
                {"role": "assistant", "content": "Hello"}
            ]
        })
        
        assert response.status_code == 500


def test_v1_query_with_metadata(client):
    """Test /v1/query with metadata."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={
            "result": "Success"
        })
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/query", json={
            "prompt": "Test prompt",
            "metadata": {"version": "1.0", "source": "test"}
        })
        
        assert response.status_code == 200


def test_legacy_run_endpoint(client):
    """Test the legacy /run endpoint still works."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={
            "result": "Success"
        })
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/run", json={
            "prompt": "Test task"
        })
        
        assert response.status_code == 200


def test_chat_completions_uses_implementation_as_fallback(client):
    """Test that chat completions uses implementation when review is not available."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={
            "plan": "Plan",
            "implementation": "Implementation content"
        })
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/chat/completions", json={
            "model": "local",
            "messages": [{"role": "user", "content": "Code this"}]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["choices"][0]["message"]["content"] == "Implementation content"


def test_query_endpoint_includes_proper_id(client):
    """Test that query endpoint returns a proper UUID-based ID."""
    with patch("api.routes.get_orchestrator") as mock_get_orch:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(return_value={"result": "test"})
        mock_get_orch.return_value = mock_orch
        
        response = client.post("/v1/query", json={
            "prompt": "Test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("query-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
