"""Tests for the unified ``llmswap mcp`` command."""

import sys
from unittest.mock import patch

from llmswap.app import main


def test_mcp_subcommand_delegates_to_natural_language_session(monkeypatch):
    argv = [
        "llmswap",
        "mcp",
        "--provider",
        "openai",
        "--model",
        "gpt-5.6",
        "--command",
        "python",
        "server.py",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    with patch("llmswap.cli.mcp_cli.NaturalLanguageMCPSession") as session_class:
        result = main()

    session_class.assert_called_once_with(
        url=None,
        command=["python", "server.py"],
        provider="openai",
        model="gpt-5.6",
        api_key=None,
        quiet=False,
        no_color=False,
    )
    session_class.return_value.run.assert_called_once_with()
    session_class.return_value.close.assert_called_once_with()
    assert result == 0


def test_mcp_subcommand_accepts_remote_url(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["llmswap", "mcp", "--url", "https://example.test/mcp"]
    )

    with patch("llmswap.cli.mcp_cli.NaturalLanguageMCPSession") as session_class:
        assert main() == 0

    assert session_class.call_args.kwargs["url"] == "https://example.test/mcp"
    assert session_class.call_args.kwargs["command"] is None


def test_natural_language_session_close_removes_all_servers():
    from llmswap.cli.mcp_cli import NaturalLanguageMCPSession

    class FakeClient:
        def __init__(self):
            self.removed = []

        def list_mcp_servers(self):
            return ["filesystem", "database"]

        def remove_mcp_server(self, name):
            self.removed.append(name)

    session = NaturalLanguageMCPSession.__new__(NaturalLanguageMCPSession)
    session.llm_client = FakeClient()

    session.close()

    assert session.llm_client.removed == ["filesystem", "database"]


def test_mcp_session_accepts_slash_commands_without_calling_llm():
    from llmswap.cli.mcp_cli import NaturalLanguageMCPSession

    class FakeUI:
        def __init__(self):
            self.inputs = iter(["/tools", "/quit"])
            self.listed = None
            self.closed = False

        def header(self, provider, model):
            pass

        def connection_status(self, server_type, count, names):
            pass

        def user_prompt(self):
            return next(self.inputs)

        def tools_list(self, tools):
            self.listed = tools

        def goodbye(self):
            self.closed = True

    class NoCallsClient:
        def chat(self, *args, **kwargs):
            raise AssertionError("slash command was sent to the LLM")

    session = NaturalLanguageMCPSession.__new__(NaturalLanguageMCPSession)
    session.ui = FakeUI()
    session.provider = "openai"
    session.model = "gpt-5.6"
    session.server_type = "local"
    session.tools = [{"name": "read_file"}]
    session.conversation_history = []
    session.llm_client = NoCallsClient()
    session.quiet = True

    session.run()

    assert session.ui.listed == session.tools
    assert session.ui.closed is True
