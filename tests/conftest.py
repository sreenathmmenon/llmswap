import pytest
import os

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