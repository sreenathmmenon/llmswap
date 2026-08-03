"""Tests for the installation and provider readiness doctor."""

import json
import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

from llmswap.app import cmd_doctor
from llmswap.doctor import diagnose


def make_config():
    config = Mock()
    config.validate.return_value = []
    config.get.return_value = {"openai": "gpt-5.6"}
    config.config_path = "/tmp/llmswap-test-config.yaml"
    return config


def test_doctor_reports_missing_selected_provider_without_exposing_secrets():
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("llmswap.doctor._load_env_files", return_value=[]),
        patch("llmswap.doctor.get_config", return_value=make_config()),
        patch("llmswap.doctor._module_available", return_value=True),
        patch("llmswap.doctor.shutil.which", return_value="/usr/local/bin/llmswap"),
    ):
        report = diagnose(provider="openai")

    assert report["healthy"] is False
    assert report["providers"][0]["missing_env"] == ["OPENAI_API_KEY"]
    assert report["environment"]["secret_values_exposed"] is False


def test_doctor_uses_the_invoked_cli_path_for_environment_comparison():
    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "secret-value"}, clear=True),
        patch("llmswap.doctor._load_env_files", return_value=[]),
        patch("llmswap.doctor.get_config", return_value=make_config()),
        patch("llmswap.doctor._module_available", return_value=True),
        patch("llmswap.doctor.sys.argv", ["/active/bin/llmswap", "doctor"]),
        patch("llmswap.doctor.sys.executable", "/active/bin/python"),
    ):
        report = diagnose(provider="openai")

    assert report["installation"]["cli_path"] == "/active/bin/llmswap"
    assert report["installation"]["cli_matches_python"] is True


def test_doctor_resolves_symlinked_environment_paths(tmp_path):
    real_bin = tmp_path / "real" / "bin"
    real_bin.mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path / "real", target_is_directory=True)

    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "secret-value"}, clear=True),
        patch("llmswap.doctor._load_env_files", return_value=[]),
        patch("llmswap.doctor.get_config", return_value=make_config()),
        patch("llmswap.doctor._module_available", return_value=True),
        patch("llmswap.doctor.sys.argv", [str(alias / "bin" / "llmswap"), "doctor"]),
        patch("llmswap.doctor.sys.executable", str(real_bin / "python")),
    ):
        report = diagnose(provider="openai")

    assert report["installation"]["cli_matches_python"] is True


def test_doctor_live_verification_is_scoped_to_selected_provider():
    live_result = {
        "name": "openai",
        "status": "verified",
        "api_key_configured": True,
        "api_key_valid": True,
        "latency_ms": 100,
        "model": "gpt-5.6",
        "error": None,
    }
    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "secret-value"}, clear=True),
        patch("llmswap.doctor._load_env_files", return_value=[]),
        patch("llmswap.doctor.get_config", return_value=make_config()),
        patch("llmswap.doctor._module_available", return_value=True),
        patch("llmswap.doctor.shutil.which", return_value="/usr/local/bin/llmswap"),
        patch(
            "llmswap.verification.verify_provider", return_value=live_result
        ) as verify,
    ):
        report = diagnose(live=True, provider="openai", timeout=3)

    verify.assert_called_once_with("openai", timeout=3)
    assert report["healthy"] is True
    assert report["providers"][0]["status"] == "verified"
    assert "secret-value" not in json.dumps(report)


def test_doctor_json_command_returns_failure_for_unhealthy_report(capsys):
    args = SimpleNamespace(live=False, provider="openai", timeout=10, format="json")
    report = {
        "healthy": False,
        "recommendations": ["Set OPENAI_API_KEY"],
    }
    with patch("llmswap.doctor.diagnose", return_value=report):
        assert cmd_doctor(args) == 1

    assert json.loads(capsys.readouterr().out) == report
