"""Release-version consistency checks."""

import inspect
import re
from pathlib import Path

import llmswap
from llmswap.mcp.client import MCPClient


ROOT = Path(__file__).resolve().parents[1]


def test_package_and_project_versions_match():
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', project, re.MULTILINE)

    assert match is not None
    assert match.group(1) == llmswap.__version__


def test_mcp_client_reports_package_version_by_default():
    default = inspect.signature(MCPClient).parameters["client_version"].default

    assert default == llmswap.__version__
