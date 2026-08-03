"""Use OpenAI and LLMSwap MCP to inspect files and create an account brief."""

from pathlib import Path

import llmswap
from dotenv import load_dotenv
from llmswap import LLMClient


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> None:
    load_dotenv(Path.home() / ".env", override=False)
    client = LLMClient(
        provider="openai",
        model="gpt-5.6",
        fallback=False,
        workspace_enabled=False,
    )

    try:
        client.add_mcp_server(
            "filesystem",
            command=[
                "npx",
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(PROJECT_DIR / "sample_data"),
            ],
        )
        tools = client.list_mcp_tools("filesystem")
        history = [{
            "role": "user",
            "content": (
                "Inspect every file using MCP tools. Write a Markdown account "
                "brief with Customer, Current Situation, Risks, and exactly "
                "three Recommended Actions. Ground every claim in the files."
            ),
        }]
        response = client.chat(history, use_mcp=True)
        called_tools = []

        for _ in range(8):
            tool_calls = getattr(response, "tool_calls", None) or []
            if not tool_calls:
                break
            results = []
            for tool_call in tool_calls:
                called_tools.append(tool_call.name)
                handler = client._mcp_tools[tool_call.name]["handler"]
                results.append({"content": handler(tool_call.arguments)})
            history.extend(client.format_tool_results(tool_calls, results, response))
            response = client.chat(history, use_mcp=True)

        output = PROJECT_DIR / "outputs" / "account_brief.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(response.content.strip() + "\n")

        print(
            f"LLMSwap {llmswap.__version__} | {client.get_current_provider()} | "
            f"{client.get_current_model()}"
        )
        print(f"MCP tools discovered: {len(tools)}")
        print(f"Tools called: {', '.join(called_tools)}\n")
        print(response.content.strip())
        print(f"\nSaved: {output}")
    finally:
        for server_name in list(client.list_mcp_servers()):
            client.remove_mcp_server(server_name)


if __name__ == "__main__":
    main()
