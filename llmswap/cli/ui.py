#!/usr/bin/env python3
"""
Clean CLI UI - Factory Droids / Claude style
Simple, clean, professional - no boxes, just labels and content
"""

import sys
from typing import Optional


class Colors:
    """ANSI color codes"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    # Bright foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"


class CleanUI:
    """Clean, simple UI matching Factory Droids / Claude style"""

    def __init__(self, use_colors: bool = True):
        """
        Initialize UI

        Args:
            use_colors: Whether to use colors (auto-detect terminal support)
        """
        self.use_colors = use_colors and sys.stdout.isatty()

    def c(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text

    def header(self, provider: str, model: Optional[str] = None):
        """Show clean header"""
        print("=" * 70)
        title = f"llmswap MCP • {provider}"
        if model:
            title += f" • {model}"
        print(f"  {self.c(title, Colors.BOLD + Colors.CYAN)}")
        print(
            f"  {self.c('Natural language interface • Type', Colors.DIM)} {self.c('help', Colors.YELLOW)} {self.c('for commands', Colors.DIM)}"
        )
        print("=" * 70)
        print()

    def connection_status(
        self, server_type: str, tools_count: int, tools_names: list = None
    ):
        """Show connection status"""
        print(
            f"{self.c('✓', Colors.GREEN)} Connected to {self.c(server_type, Colors.BOLD)} MCP server"
        )

        tools_text = f"{tools_count} tool{'s' if tools_count != 1 else ''}"
        if tools_names and len(tools_names) <= 3:
            tools_list = ", ".join(tools_names)
            print(
                f"{self.c('✓', Colors.GREEN)} {tools_text} available: {self.c(tools_list, Colors.CYAN)}"
            )
        else:
            print(f"{self.c('✓', Colors.GREEN)} {tools_text} available")
        print()

    def user_prompt(self) -> str:
        """Show user input prompt with border like Factory Droids"""
        # Add ONE line of space above (not 3!)
        print()

        # Draw complete box FIRST
        print(self.c("╭" + "─" * 68 + "╮", Colors.BRIGHT_BLACK))
        # CRITICAL: 66 spaces between borders (not 68!)
        print(
            self.c("│ " + " " * 66 + " │", Colors.BRIGHT_BLACK)
        )  # Empty line for input
        print(self.c("╰" + "─" * 68 + "╯", Colors.BRIGHT_BLACK))

        # Move cursor up 2 lines and right 2 chars (to │ >)
        print("\033[2A\033[2C", end="", flush=True)

        # Show prompt and get input
        print(self.c("> ", Colors.BLUE), end="", flush=True)
        user_input = input().strip()

        # Move cursor down to below the box
        print("\033[2B", end="")
        # Only ONE blank line after input box
        print()

        return user_input

    def tool_execution(self, tool_name: str, duration: Optional[float] = None):
        """Show tool execution status"""
        if duration is not None:
            print(
                f"  {self.c('→', Colors.BRIGHT_BLACK)} {self.c(tool_name, Colors.YELLOW)} {self.c('✓', Colors.GREEN)} {self.c(f'({duration:.2f}s)', Colors.DIM)}"
            )
        else:
            print(
                f"  {self.c('→', Colors.BRIGHT_BLACK)} {self.c(tool_name, Colors.YELLOW)} {self.c('...', Colors.DIM)}",
                flush=True,
            )
        print()

    def assistant_response(self, content: str):
        """Show assistant response with border like Factory Droids"""
        # Only ONE blank line above
        print()

        # Top border
        print(self.c("╭" + "─" * 68 + "╮", Colors.BRIGHT_BLACK))

        # Content with borders - each line gets left and right border
        for line in content.split("\n"):
            # Handle empty lines
            if not line.strip():
                print(
                    self.c("│", Colors.BRIGHT_BLACK)
                    + " " * 68
                    + self.c("│", Colors.BRIGHT_BLACK)
                )
                continue

            # Wrap long lines to 66 chars max
            if len(line) <= 66:
                # CRITICAL: Use ljust to ensure EXACTLY 66 chars with padding
                padded_line = line.ljust(66)
                print(
                    self.c("│ ", Colors.BRIGHT_BLACK)
                    + padded_line
                    + self.c(" │", Colors.BRIGHT_BLACK)
                )
            else:
                # Simple word wrap
                words = line.split(" ")
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 66:
                        current_line += (" " if current_line else "") + word
                    else:
                        if current_line:
                            # CRITICAL: Use ljust to ensure EXACTLY 66 chars
                            padded_line = current_line.ljust(66)
                            print(
                                self.c("│ ", Colors.BRIGHT_BLACK)
                                + padded_line
                                + self.c(" │", Colors.BRIGHT_BLACK)
                            )
                        current_line = word
                if current_line:
                    # CRITICAL: Use ljust to ensure EXACTLY 66 chars
                    padded_line = current_line.ljust(66)
                    print(
                        self.c("│ ", Colors.BRIGHT_BLACK)
                        + padded_line
                        + self.c(" │", Colors.BRIGHT_BLACK)
                    )

        # Bottom border
        print(self.c("╰" + "─" * 68 + "╯", Colors.BRIGHT_BLACK))

        # Only ONE blank line after response (not 2!)
        print()

    def error(self, message: str):
        """Show error message"""
        print(
            f"{self.c('✗', Colors.RED)} {self.c('Error:', Colors.BOLD + Colors.RED)} {message}"
        )
        print()

    def warning(self, message: str):
        """Show warning message"""
        print(
            f"{self.c('⚠', Colors.YELLOW)} {self.c('Warning:', Colors.BOLD + Colors.YELLOW)} {message}"
        )
        print()

    def info(self, message: str):
        """Show info message"""
        print(f"{self.c('ℹ', Colors.BLUE)} {message}")
        print()

    def goodbye(self):
        """Show goodbye message"""
        print(self.c("👋 Goodbye! Thanks for using llmswap MCP.", Colors.CYAN))
        print()

    def help_message(self):
        """Show help message"""
        print(self.c("Available Commands:", Colors.BOLD + Colors.CYAN))
        print()

        commands = [
            ("help", "Show this help message"),
            ("tools", "List all available tools"),
            ("clear", "Clear conversation history"),
            ("status", "Show connection status"),
            ("exit", "Exit the CLI (or use: quit, bye)"),
        ]

        for cmd, desc in commands:
            print(f"  {self.c(cmd.ljust(10), Colors.YELLOW)} {desc}")
        print()

    def tools_list(self, tools: list):
        """Show available tools"""
        print(self.c("Available Tools:", Colors.BOLD + Colors.CYAN))
        print()

        if not tools:
            print(f"  {self.c('No tools available', Colors.DIM)}")
        else:
            for i, tool in enumerate(tools, 1):
                name = tool.get("name", "unknown")
                desc = tool.get("description", "No description")

                print(
                    f"  {self.c(f'{i}.', Colors.DIM)} {self.c(name, Colors.BOLD + Colors.YELLOW)}"
                )
                print(f"     {self.c(desc, Colors.DIM)}")
                if i < len(tools):
                    print()
        print()

    def thinking(self, message: str = "Thinking"):
        """Show thinking message"""
        print(
            f"{self.c('⚙', Colors.CYAN)} {self.c(message, Colors.DIM)}...",
            end="",
            flush=True,
        )

    def thinking_done(self):
        """Clear thinking message"""
        print("\r" + " " * 60 + "\r", end="", flush=True)


class SimpleUI(CleanUI):
    """Simple UI without colors - inherits from CleanUI"""

    def __init__(self):
        super().__init__(use_colors=False)

    def user_prompt(self) -> str:
        """Simple user prompt without borders for fallback"""
        user_input = input(self.c("> ", Colors.BLUE)).strip()
        print()
        return user_input

    def assistant_response(self, content: str):
        """Simple response without borders for fallback"""
        for line in content.split("\n"):
            print(f"  {line}")
        print()
