"""Provider-status CLI regressions."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from llmswap.app import cmd_providers


def test_provider_status_reports_missing_configured_ollama_model(capsys):
    config = Mock()
    config.get.return_value = {
        "ollama": "configured-but-missing:latest",
    }
    response = Mock(status_code=200)
    response.json.return_value = {
        "models": [{"name": "llama3.2:latest", "model": "llama3.2:latest"}]
    }
    args = SimpleNamespace(verify=False, format="json", provider=None, timeout=10)

    with (
        patch("llmswap.app.get_config", return_value=config),
        patch("requests.get", return_value=response),
    ):
        assert cmd_providers(args) == 0

    output = json.loads(capsys.readouterr().out)
    ollama = next(row for row in output["providers"] if row[0] == "OLLAMA")
    assert ollama[2] == "⚠️ MODEL MISSING"
    assert ollama[3] == "Run: ollama pull configured-but-missing:latest"
