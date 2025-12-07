#!/usr/bin/env python3
"""
MCP CLI Tool - Natural language interface for MCP servers

Usage:
    llmswap-mcp --command "python server.py"
    llmswap-mcp --url https://api.example.com/mcp
    llmswap-mcp --command npx -y @modelcontextprotocol/server-filesystem /tmp

The CLI uses natural language - just type what you want to do:
    > You: What is 2 + 2?
    > You: Show me files in /tmp
    > You: Read the file data.txt
"""

import os
import sys
import json
import argparse
import time
from typing import Optional, Dict, Any, List
import readline  # For command history

try:
    from .ui import CleanUI, SimpleUI
except ImportError:
    from llmswap.cli.ui import CleanUI, SimpleUI


class NaturalLanguageMCPSession:
    """Natural language MCP CLI session using LLM for interpretation"""

    def __init__(
        self,
        url: Optional[str] = None,
        command: Optional[List[str]] = None,
        provider: str = "auto",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        quiet: bool = False,
        no_color: bool = False,
    ):
        """
        Initialize natural language MCP session

        Args:
            url: URL for remote MCP server
            command: Command for local MCP server
            provider: LLM provider (auto, anthropic, openai, gemini, groq, xai)
            model: Model name (optional)
            api_key: API key (optional, uses env vars)
            quiet: Quiet mode (minimal output)
            no_color: Disable colors
        """
        from ..client import LLMClient
        from ..exceptions import ConfigurationError

        self.quiet = quiet
        self.conversation_history = []
        self.llm_client = None
        self.server_name = "main"
        self.tools = []
        self.provider = provider
        self.model = model

        # Initialize UI
        if no_color or not sys.stdout.isatty():
            self.ui = SimpleUI()
        else:
            self.ui = CleanUI(use_colors=True)

        # Initialize LLM client
        if not self.quiet:
            self.ui.thinking("Initializing LLM")

        try:
            self.llm_client = LLMClient(
                provider=provider, model=model, api_key=api_key, fallback=True
            )
            if not self.quiet:
                self.ui.thinking_done()
        except ConfigurationError as e:
            if not self.quiet:
                self.ui.thinking_done()
            self.ui.error(f"LLM initialization failed: {e}")
            self._show_api_key_help(provider)
            sys.exit(1)

        # Connect to MCP server
        try:
            if command:
                self.server_type = "local"
                if not self.quiet:
                    self.ui.thinking("Connecting to local MCP server")
                self.llm_client.add_mcp_server(self.server_name, command=command)
            elif url:
                self.server_type = "remote"
                if not self.quiet:
                    self.ui.thinking("Connecting to remote MCP server")
                self.llm_client.add_mcp_server(self.server_name, url=url)
            else:
                self.ui.error("Must provide either --url or --command")
                sys.exit(1)

            if not self.quiet:
                self.ui.thinking_done()

            # Discover tools
            self._discover_tools()

        except Exception as e:
            if not self.quiet:
                self.ui.thinking_done()
            self.ui.error(f"MCP connection failed: {e}")
            sys.exit(1)

    def _discover_tools(self):
        """Discover tools from MCP server"""
        try:
            self.tools = self.llm_client.list_mcp_tools(self.server_name)
        except Exception as e:
            if not self.quiet:
                self.ui.warning(f"Could not list tools: {e}")

    def _show_api_key_help(self, provider: str):
        """Show help for setting up API keys"""
        print("To use this CLI, you need an API key for your chosen LLM provider.")
        print()
        print("You can provide it in two ways:")
        print()
        print("1. Via command line:")
        print(f"   llmswap-mcp --provider {provider} --api-key YOUR_KEY --command ...")
        print()
        print("2. Via environment variable (recommended):")

        if provider == "anthropic" or provider == "auto":
            print("   export ANTHROPIC_API_KEY=your_key_here")
        if provider == "openai" or provider == "auto":
            print("   export OPENAI_API_KEY=your_key_here")
        if provider == "gemini" or provider == "auto":
            print("   export GEMINI_API_KEY=your_key_here")
        if provider == "groq" or provider == "auto":
            print("   export GROQ_API_KEY=your_key_here")
        if provider == "xai" or provider == "auto":
            print("   export XAI_API_KEY=your_key_here")

        print()
        print("Get your API key from:")
        print("  - Anthropic: https://console.anthropic.com/")
        print("  - OpenAI: https://platform.openai.com/api-keys")
        print("  - Google Gemini: https://aistudio.google.com/app/apikey")
        print("  - Groq: https://console.groq.com/")
        print("  - X.AI: https://x.ai/api")
        print()

    def run(self):
        """Run natural language conversation loop"""
        # Show header
        self.ui.header(self.provider, self.model)

        # Show connection status
        tool_names = [t.get("name") for t in self.tools[:3]]
        self.ui.connection_status(self.server_type, len(self.tools), tool_names)

        while True:
            try:
                # Get user input with beautiful prompt
                user_input = self.ui.user_prompt().strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() == "help":
                    self.ui.help_message()
                    continue

                if user_input.lower() == "tools":
                    self.ui.tools_list(self.tools)
                    continue

                if user_input.lower() == "clear":
                    self.conversation_history = []
                    self.ui.info("Conversation history cleared")
                    continue

                if user_input.lower() == "status":
                    self.ui.connection_status(
                        self.server_type,
                        len(self.tools),
                        [t.get("name") for t in self.tools[:5]],
                    )
                    continue

                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    self.ui.goodbye()
                    break

                # Add to conversation history
                self.conversation_history.append(
                    {"role": "user", "content": user_input}
                )

                # Send to LLM with MCP tools enabled - with tool calling loop
                try:
                    # Initial LLM call
                    start_time = time.time()
                    response = self.llm_client.chat(
                        self.conversation_history, use_mcp=True
                    )

                    # Tool calling loop - continue until no more tool calls
                    max_iterations = 5  # Prevent infinite loops
                    iteration = 0

                    while (
                        hasattr(response, "tool_calls")
                        and response.tool_calls
                        and iteration < max_iterations
                    ):
                        iteration += 1

                        # Show tool execution
                        for tool_call in response.tool_calls:
                            # tool_call is a ToolCall dataclass, not a dict
                            if isinstance(tool_call, dict):
                                tool_name = tool_call.get("name", "unknown")
                            else:
                                tool_name = getattr(tool_call, "name", "unknown")

                            tool_start = time.time()

                        # Execute tools and collect results
                        executed_results = []
                        for tool_call in response.tool_calls:
                            try:
                                # Get tool name and arguments
                                if isinstance(tool_call, dict):
                                    tool_name = tool_call.get("name")
                                    tool_args = tool_call.get("arguments", {})
                                else:
                                    tool_name = getattr(tool_call, "name")
                                    tool_args = getattr(tool_call, "arguments", {})

                                tool_exec_start = time.time()

                                # Execute MCP tool via LLMClient's internal method
                                if tool_name in self.llm_client._mcp_tools:
                                    tool_info = self.llm_client._mcp_tools[tool_name]
                                    result = tool_info["handler"](tool_args)
                                    executed_results.append({"content": result})

                                    # Show completion
                                    duration = time.time() - tool_exec_start
                                    if not self.quiet:
                                        self.ui.tool_execution(tool_name, duration)
                                else:
                                    # Tool not found
                                    executed_results.append(
                                        {
                                            "content": f"Error: Tool '{tool_name}' not found"
                                        }
                                    )
                                    if not self.quiet:
                                        self.ui.error(f"Tool '{tool_name}' not found")
                            except Exception as e:
                                # Tool execution failed
                                executed_results.append({"content": f"Error: {str(e)}"})
                                if not self.quiet:
                                    self.ui.error(f"Tool execution failed: {e}")

                        # Format tool results using provider-specific formatter
                        formatted_messages = self.llm_client.format_tool_results(
                            response.tool_calls, executed_results, response
                        )

                        # Add formatted messages to conversation history
                        self.conversation_history.extend(formatted_messages)

                        # Continue conversation with tool results
                        response = self.llm_client.chat(
                            self.conversation_history, use_mcp=True
                        )

                    # Final response (no more tool calls)
                    self.conversation_history.append(
                        {"role": "assistant", "content": response.content}
                    )

                    # Show response
                    self.ui.assistant_response(response.content)

                except Exception as e:
                    self.ui.error(str(e))
                    # Don't add failed exchanges to history
                    self.conversation_history.pop()  # Remove user message

            except KeyboardInterrupt:
                print()
                self.ui.goodbye()
                break
            except EOFError:
                print()
                self.ui.goodbye()
                break
            except Exception as e:
                self.ui.error(f"Unexpected error: {e}")

    def close(self):
        """Close connections"""
        # LLMClient handles cleanup automatically
        pass


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Natural Language MCP Client - Chat with MCP servers using natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect to local MCP server with Anthropic
  llmswap-mcp --command python mcp_server.py
  
  # Connect to filesystem server
  llmswap-mcp --command npx -y @modelcontextprotocol/server-filesystem /tmp
  
  # Use specific provider and model
  llmswap-mcp --provider openai --model gpt-4 --command python server.py
  
  # Connect to remote server
  llmswap-mcp --url https://api.example.com/mcp
  
  # Quiet mode (minimal output)
  llmswap-mcp --quiet --command python server.py

Environment Variables:
  ANTHROPIC_API_KEY  - API key for Anthropic Claude
  OPENAI_API_KEY     - API key for OpenAI GPT
  GEMINI_API_KEY     - API key for Google Gemini
  GROQ_API_KEY       - API key for Groq
  XAI_API_KEY        - API key for X.AI Grok
        """,
    )

    # MCP connection arguments
    parser.add_argument("--url", help="URL of remote MCP server")

    parser.add_argument(
        "--command",
        help="Command to start local MCP server",
        nargs=argparse.REMAINDER,
        metavar="CMD",
    )

    # LLM provider arguments
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "anthropic", "openai", "gemini", "groq", "xai"],
        help="LLM provider to use (default: auto-detect)",
    )

    parser.add_argument(
        "--model", help="Specific model name (optional, uses provider defaults)"
    )

    parser.add_argument(
        "--api-key",
        help="API key for LLM provider (optional, uses environment variables)",
    )

    # UI arguments
    parser.add_argument(
        "--quiet", action="store_true", help="Quiet mode - minimal output"
    )

    parser.add_argument(
        "--no-color", action="store_true", help="Disable colors and fancy UI"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.url and not args.command:
        parser.error("Must provide either --url or --command")

    if args.url and args.command:
        parser.error("Cannot provide both --url and --command")

    # Start natural language session
    session = NaturalLanguageMCPSession(
        url=args.url,
        command=args.command,
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        quiet=args.quiet,
        no_color=args.no_color,
    )

    try:
        session.run()
    finally:
        session.close()


if __name__ == "__main__":
    main()
