import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_URL", raising=False)

@pytest.fixture
def setup_anthropic_env(monkeypatch):
    """Setup Anthropic environment"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

@pytest.fixture
def setup_openai_env(monkeypatch):
    """Setup OpenAI environment"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

@pytest.fixture
def setup_gemini_env(monkeypatch):
    """Setup Gemini environment"""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

# Web UI test fixtures

@pytest.fixture
def temp_workspace_dir():
    """Create temporary workspace directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_llm_client():
    """Mock LLMClient for web tests"""
    client = Mock()
    client.query = Mock(return_value="Mock response from model")
    client.query_stream = Mock(return_value=iter(["chunk1", "chunk2"]))
    client.get_current_provider = Mock(return_value="openai")
    client.list_available_providers = Mock(return_value=["openai", "anthropic"])
    return client

@pytest.fixture
def mock_workspace():
    """Mock Workspace for web tests"""
    workspace = Mock()
    workspace.name = "test-workspace"
    workspace.path = Path("/tmp/test-workspace")
    workspace.log_interaction = Mock()
    workspace.get_journal = Mock(return_value=[])
    workspace.get_stats = Mock(return_value={
        'total_queries': 10,
        'total_cost': 0.05,
        'comparisons': 3
    })
    return workspace

@pytest.fixture
def sample_comparison_data():
    """Sample comparison data for testing"""
    return {
        'prompt': 'What is 2+2?',
        'timestamp': '2024-10-05T10:00:00',
        'results': [
            {
                'model': 'gpt-4',
                'response': '2+2 equals 4.',
                'time': 1.23,
                'tokens': 8,
                'cost': 0.002
            },
            {
                'model': 'claude-3-5-sonnet-20241022',
                'response': 'The answer is 4.',
                'time': 1.15,
                'tokens': 7,
                'cost': 0.0015
            }
        ]
    }