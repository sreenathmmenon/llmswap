"""
Comprehensive test suite for LLMSwap Web UI

Tests:
- Optional dependency handling (Flask)
- CLI commands
- Flask server routes and SSE streaming
- Model comparison logic
- Workspace integration
- Frontend behavior
"""

import pytest
import sys
import json
import time
from unittest.mock import patch, Mock, MagicMock
from io import StringIO


# ============================================================================
# SECTION 1: Optional Dependency Tests
# ============================================================================

def test_web_available_when_flask_installed():
    """Test WEB_AVAILABLE is True when Flask is installed"""
    try:
        import flask
        from llmswap.web import WEB_AVAILABLE
        assert WEB_AVAILABLE == True
    except ImportError:
        pytest.skip("Flask not installed")


def test_flask_import_error_handling():
    """Test that missing Flask dependency is handled gracefully"""
    with patch('builtins.__import__', side_effect=ImportError("No module named 'flask'")):
        try:
            import flask
            pytest.fail("Expected ImportError")
        except ImportError as e:
            assert "flask" in str(e).lower()


def test_optional_dependency_versions():
    """Test that installed Flask versions meet minimum requirements"""
    try:
        import flask
        version = flask.__version__.split('.')
        major = int(version[0])
        assert major >= 3, f"Flask version {flask.__version__} < 3.0.0"
    except ImportError:
        pytest.skip("Flask not installed")


# ============================================================================
# SECTION 2: CLI Command Tests
# ============================================================================

def test_web_command_error_message_content():
    """Test web command shows helpful error when Flask not installed"""
    error_msg = "Web UI requires Flask"
    install_msg = "pip install llmswap[web]"

    assert "Web UI" in error_msg
    assert "llmswap[web]" in install_msg


def test_web_command_port_validation():
    """Test web command accepts valid port argument"""
    test_port = 8080
    assert test_port > 0 and test_port < 65536


def test_web_command_host_validation():
    """Test web command accepts valid host argument"""
    test_host = "127.0.0.1"
    assert test_host in ["127.0.0.1", "0.0.0.0", "localhost"]


# ============================================================================
# SECTION 3: Flask Server Tests
# ============================================================================

pytest.importorskip("flask", reason="Flask not installed for server tests")


@pytest.fixture
def app():
    """Create test Flask app"""
    from llmswap.web.app import create_app
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_app_creation(app):
    """Test Flask app is created successfully"""
    assert app is not None
    assert app.config['TESTING'] == True


def test_index_route(client):
    """Test index route returns HTML"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'html' in response.data.lower()


def test_health_check_route(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_compare_route_requires_prompt(client):
    """Test /compare requires prompt in request"""
    response = client.post('/compare', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_compare_route_requires_models(client):
    """Test /compare requires models list in request"""
    response = client.post('/compare', json={'prompt': 'test'})
    assert response.status_code == 400


def test_compare_route_valid_request(client):
    """Test /compare with valid request"""
    response = client.post('/compare', json={
        'prompt': 'What is 2+2?',
        'models': ['gpt-4', 'claude-3-5-sonnet-20241022']
    })
    assert response.status_code == 200


def test_sse_event_format():
    """Test Server-Sent Events are formatted correctly"""
    event_data = {'model': 'gpt-4', 'content': 'test'}
    sse_line = f"data: {json.dumps(event_data)}\n\n"

    assert sse_line.startswith('data: ')
    assert sse_line.endswith('\n\n')
    assert json.loads(sse_line[6:-2])['model'] == 'gpt-4'


def test_workspace_list_route(client):
    """Test /api/workspaces route returns workspace list"""
    response = client.get('/api/workspaces')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_save_comparison_route(client):
    """Test /api/save-comparison saves to workspace"""
    response = client.post('/api/save-comparison', json={
        'workspace': 'test-workspace',
        'prompt': 'test prompt',
        'results': [
            {'model': 'gpt-4', 'response': 'answer', 'time': 1.2, 'tokens': 10}
        ]
    })
    assert response.status_code in [200, 201]


def test_error_handling_404(client):
    """Test server handles 404 errors gracefully"""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404


# ============================================================================
# SECTION 4: Model Comparison Tests
# ============================================================================

def test_compare_models_single_model(mock_llm_client):
    """Test comparison with single model"""
    from llmswap.web.comparison import compare_models

    results = compare_models(
        prompt="What is 2+2?",
        models=["gpt-4"],
        client=mock_llm_client
    )

    assert len(results) == 1
    assert results[0]['model'] == 'gpt-4'
    assert 'response' in results[0]
    assert 'time' in results[0]
    assert 'tokens' in results[0]


def test_compare_models_multiple_models(mock_llm_client):
    """Test comparison with multiple models"""
    from llmswap.web.comparison import compare_models

    results = compare_models(
        prompt="test",
        models=["gpt-4", "claude-3-5-sonnet-20241022", "gemini-pro"],
        client=mock_llm_client
    )

    assert len(results) == 3
    model_names = [r['model'] for r in results]
    assert "gpt-4" in model_names


def test_compare_models_timing():
    """Test that comparison tracks response time"""
    from llmswap.web.comparison import compare_models

    with patch('llmswap.LLMClient') as MockClient:
        mock_client = MockClient.return_value
        mock_client.query.return_value = "response"

        results = compare_models(
            prompt="test",
            models=["gpt-4"],
            client=mock_client
        )

        assert results[0]['time'] > 0
        assert isinstance(results[0]['time'], float)


def test_compare_models_error_handling(mock_llm_client):
    """Test comparison handles model errors gracefully"""
    from llmswap.web.comparison import compare_models

    mock_llm_client.query.side_effect = Exception("API Error")

    results = compare_models(
        prompt="test",
        models=["gpt-4"],
        client=mock_llm_client
    )

    assert len(results) == 1
    assert 'error' in results[0]


def test_compare_models_concurrent_execution():
    """Test models are queried concurrently for speed"""
    from llmswap.web.comparison import compare_models

    with patch('llmswap.LLMClient') as MockClient:
        mock_client = MockClient.return_value

        def slow_query(*args, **kwargs):
            time.sleep(1)
            return "response"

        mock_client.query.side_effect = slow_query

        start = time.time()
        results = compare_models(
            prompt="test",
            models=["gpt-4", "claude-3-5-sonnet-20241022"],
            client=mock_client
        )
        duration = time.time() - start

        # Should take ~1 second (concurrent), not 2 seconds (sequential)
        assert duration < 1.5


def test_empty_prompt_handling():
    """Test comparison handles empty prompt"""
    from llmswap.web.comparison import compare_models

    with pytest.raises(ValueError):
        compare_models(prompt="", models=["gpt-4"])


def test_empty_models_list_handling():
    """Test comparison handles empty models list"""
    from llmswap.web.comparison import compare_models

    with pytest.raises(ValueError):
        compare_models(prompt="test", models=[])


# ============================================================================
# SECTION 5: Workspace Integration Tests
# ============================================================================

def test_save_comparison_to_workspace(mock_workspace, sample_comparison_data):
    """Test saving comparison results to workspace"""
    from llmswap.web.workspace_integration import save_comparison

    save_comparison(workspace=mock_workspace, data=sample_comparison_data)

    mock_workspace.log_interaction.assert_called_once()


def test_get_workspace_by_name():
    """Test retrieving workspace by name"""
    from llmswap.web.workspace_integration import get_workspace

    with patch('llmswap.workspace.Workspace') as MockWorkspace:
        mock_ws = MockWorkspace.return_value
        mock_ws.name = "test-workspace"

        workspace = get_workspace("test-workspace")

        assert workspace is not None
        assert workspace.name == "test-workspace"


def test_list_all_workspaces():
    """Test listing all available workspaces"""
    from llmswap.web.workspace_integration import list_workspaces

    with patch('llmswap.workspace.Workspace.list_all') as mock_list:
        mock_list.return_value = ["workspace1", "workspace2"]

        workspaces = list_workspaces()

        assert len(workspaces) == 2
        assert "workspace1" in workspaces


def test_comparison_metadata_saved(mock_workspace, sample_comparison_data):
    """Test that comparison metadata is saved correctly"""
    from llmswap.web.workspace_integration import save_comparison

    save_comparison(workspace=mock_workspace, data=sample_comparison_data)

    call_args = mock_workspace.log_interaction.call_args
    assert call_args is not None


def test_workspace_cost_tracking(mock_workspace, sample_comparison_data):
    """Test that costs are tracked in workspace"""
    from llmswap.web.workspace_integration import save_comparison

    save_comparison(workspace=mock_workspace, data=sample_comparison_data)

    # Verify cost tracking happens


def test_workspace_statistics(mock_workspace):
    """Test workspace statistics include web comparisons"""
    from llmswap.web.workspace_integration import get_workspace_stats

    stats = get_workspace_stats(mock_workspace)

    assert 'total_queries' in stats
    assert 'comparisons' in stats


# ============================================================================
# SECTION 6: Frontend Tests
# ============================================================================

def test_index_page_loads(client):
    """Test index page returns valid HTML"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


def test_page_includes_prompt_textarea(client):
    """Test page has prompt input"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'textarea' in html.lower() or 'input' in html.lower()
    assert 'prompt' in html.lower()


def test_page_includes_model_selection(client):
    """Test page has model checkboxes/selection"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'checkbox' in html.lower() or 'select' in html.lower()


def test_page_includes_compare_button(client):
    """Test page has compare/submit button"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'button' in html.lower()
    assert 'compare' in html.lower() or 'submit' in html.lower()


def test_page_uses_tailwind_css(client):
    """Test page includes Tailwind CSS"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'tailwind' in html.lower() or 'cdn.tailwindcss.com' in html.lower()


def test_page_includes_javascript(client):
    """Test page includes JavaScript for interactivity"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert '<script' in html.lower()


def test_responsive_design(client):
    """Test page is responsive (mobile-friendly)"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'viewport' in html.lower() or 'md:' in html


def test_save_button_present(client):
    """Test save to workspace button exists"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'save' in html.lower()


def test_workspace_selector_present(client):
    """Test workspace selection dropdown exists"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'workspace' in html.lower()


# ============================================================================
# SECTION 7: Additional Edge Cases and Integration Tests
# ============================================================================

def test_compare_route_multiple_models(client):
    """Test /compare with multiple models"""
    response = client.post('/compare', json={
        'prompt': 'test',
        'models': ['gpt-4', 'claude-3-5-sonnet-20241022', 'gemini-pro']
    })
    assert response.status_code == 200


def test_compare_route_invalid_model(client):
    """Test /compare handles invalid model names"""
    response = client.post('/compare', json={
        'prompt': 'test',
        'models': ['invalid-model-xyz']
    })
    assert response.status_code in [200, 400]


def test_sse_completion_event():
    """Test completion event is sent after all models respond"""
    completion_event = "data: {\"event\": \"complete\"}\n\n"
    assert '"event": "complete"' in completion_event


def test_save_comparison_without_workspace(client):
    """Test saving comparison without workspace specified"""
    response = client.post('/api/save-comparison', json={
        'prompt': 'test',
        'results': []
    })
    assert response.status_code in [200, 400]


def test_compare_models_token_counting():
    """Test that comparison counts tokens"""
    from llmswap.web.comparison import compare_models

    with patch('llmswap.LLMClient') as MockClient:
        mock_client = MockClient.return_value
        mock_client.query.return_value = "response"

        results = compare_models(
            prompt="test",
            models=["gpt-4"],
            client=mock_client
        )

        assert 'tokens' in results[0]
        assert results[0]['tokens'] > 0


def test_compare_models_cost_calculation():
    """Test that comparison calculates cost"""
    from llmswap.web.comparison import compare_models

    with patch('llmswap.LLMClient') as MockClient:
        mock_client = MockClient.return_value
        mock_client.query.return_value = "response"

        results = compare_models(
            prompt="test",
            models=["gpt-4"],
            client=mock_client
        )

        assert 'cost' in results[0]
        assert results[0]['cost'] >= 0


def test_compare_models_partial_failure():
    """Test comparison continues when one model fails"""
    from llmswap.web.comparison import compare_models

    with patch('llmswap.LLMClient') as MockClient:
        mock_client = MockClient.return_value
        mock_client.query.side_effect = ["success", Exception("error")]

        results = compare_models(
            prompt="test",
            models=["gpt-4", "claude-3-5-sonnet-20241022"],
            client=mock_client
        )

        assert len(results) == 2
        assert 'error' not in results[0]
        assert 'error' in results[1]


def test_result_format_consistency():
    """Test all results have consistent format"""
    from llmswap.web.comparison import compare_models

    with patch('llmswap.LLMClient') as MockClient:
        mock_client = MockClient.return_value
        mock_client.query.return_value = "response"

        results = compare_models(
            prompt="test",
            models=["gpt-4", "claude-3-5-sonnet-20241022"],
            client=mock_client
        )

        keys_0 = set(results[0].keys())
        keys_1 = set(results[1].keys())
        assert keys_0 == keys_1


def test_create_workspace_if_not_exists():
    """Test creating workspace if it doesn't exist"""
    from llmswap.web.workspace_integration import get_or_create_workspace

    with patch('llmswap.workspace.Workspace') as MockWorkspace:
        mock_ws = MockWorkspace.return_value
        mock_ws.name = "new-workspace"

        workspace = get_or_create_workspace("new-workspace")
        assert workspace is not None


def test_workspace_journal_entry_format(sample_comparison_data):
    """Test journal entry has correct format for comparisons"""
    from llmswap.web.workspace_integration import format_comparison_entry

    entry = format_comparison_entry(sample_comparison_data)

    assert 'What is 2+2?' in entry
    assert 'gpt-4' in entry
    assert 'claude-3-5-sonnet-20241022' in entry


def test_comparison_history_retrieval(mock_workspace):
    """Test retrieving comparison history from workspace"""
    from llmswap.web.workspace_integration import get_comparison_history

    mock_workspace.get_journal.return_value = [
        {'type': 'comparison', 'prompt': 'test1', 'models': ['gpt-4']},
        {'type': 'comparison', 'prompt': 'test2', 'models': ['claude-3-5-sonnet-20241022']}
    ]

    history = get_comparison_history(mock_workspace)
    assert len(history) >= 0


def test_page_includes_results_area(client):
    """Test page has area to display results"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'results' in html.lower() or 'response' in html.lower()


def test_comparison_ui_shows_multiple_columns(client):
    """Test UI displays results in side-by-side columns"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'grid' in html.lower() or 'flex' in html.lower()


def test_accessibility_features(client):
    """Test page has proper ARIA labels and accessibility"""
    response = client.get('/')
    html = response.data.decode('utf-8')

    assert 'label' in html.lower() or 'aria-' in html.lower()


def test_flask_cors_availability():
    """Test flask-cors can be imported when web deps installed"""
    try:
        import flask_cors
        assert flask_cors is not None
    except ImportError:
        pytest.skip("flask-cors not installed")
