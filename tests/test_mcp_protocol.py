"""MCP protocol lifecycle regressions."""

from llmswap.mcp.client import MCPClient
from llmswap.mcp.protocol import MCPProtocol


class FakeTransport:
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)

    def receive_message(self, timeout=None):
        return {
            "jsonrpc": "2.0",
            "id": self.messages[0]["id"],
            "result": {
                "protocolVersion": MCPProtocol.PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "test-server", "version": "1.0"},
            },
        }


class InterleavedTransport:
    def __init__(self, response_id):
        self.messages = []
        self.incoming = [
            {"jsonrpc": "2.0", "method": "notifications/tools/list_changed"},
            {
                "jsonrpc": "2.0",
                "id": response_id,
                "result": {"tools": []},
            },
        ]

    def send_message(self, message):
        self.messages.append(message)

    def receive_message(self, timeout=None):
        return self.incoming.pop(0)


def test_initialize_uses_current_protocol_and_sends_initialized_notification():
    client = MCPClient()
    client.transport = FakeTransport()

    client._initialize()

    initialize, initialized = client.transport.messages
    assert initialize["method"] == "initialize"
    assert initialize["params"]["protocolVersion"] == "2025-11-25"
    assert initialized == {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
    }
    assert client._initialized is True


def test_response_matching_skips_interleaved_notifications():
    client = MCPClient()
    client._initialized = True
    request_id = "tools-request"
    client.transport = InterleavedTransport(request_id)

    response = client._receive_response(request_id)

    assert response.result == {"tools": []}
