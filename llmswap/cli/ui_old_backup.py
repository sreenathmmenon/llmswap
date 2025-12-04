#!/usr/bin/env python3
"""
Beautiful CLI UI components inspired by Factory Droids
"""

import sys
import time
from typing import Optional


class Colors:
    """ANSI color codes"""
    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'


class UI:
    """Beautiful UI components for MCP CLI"""
    
    def __init__(self, use_colors: bool = True, width: int = 70):
        """
        Initialize UI
        
        Args:
            use_colors: Whether to use colors (detect terminal support)
            width: Width of UI elements
        """
        self.use_colors = use_colors and sys.stdout.isatty()
        self.width = width
    
    def color(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def header(self, provider: str, model: Optional[str] = None):
        """Show beautiful header"""
        # Top border
        print("╭" + "─" * (self.width - 2) + "╮")
        
        # Title line
        title = "⚡ llmswap MCP Client"
        provider_info = f"Provider: {provider}"
        if model:
            provider_info = f"{provider}/{model}"
        
        spaces = self.width - 4 - len(title) - len(provider_info)
        print(f"│ {self.color(title, Colors.BOLD + Colors.CYAN)}{' ' * spaces}{self.color(provider_info, Colors.BRIGHT_BLACK)} │")
        
        # Subtitle
        subtitle = "Natural language interface • Type 'help' for commands"
        padding = (self.width - 4 - len(subtitle)) // 2
        print(f"│ {' ' * padding}{self.color(subtitle, Colors.DIM)}{' ' * (self.width - 4 - len(subtitle) - padding)} │")
        
        # Bottom border
        print("╰" + "─" * (self.width - 2) + "╯")
        print()
    
    def connection_status(self, server_type: str, tools_count: int, tools_names: list = None):
        """Show connection status"""
        # Connection info
        print(f"{self.color('✓', Colors.GREEN)} Connected to {self.color(server_type, Colors.BOLD)} MCP server")
        
        # Tools info
        tools_text = f"{tools_count} tool{'s' if tools_count != 1 else ''}"
        if tools_names and len(tools_names) <= 3:
            tools_list = ", ".join(tools_names)
            print(f"{self.color('✓', Colors.GREEN)} {self.color(tools_text, Colors.BOLD)} discovered: {self.color(tools_list, Colors.CYAN)}")
        else:
            print(f"{self.color('✓', Colors.GREEN)} {self.color(tools_text, Colors.BOLD)} available")
        
        print()
    
    def user_prompt(self) -> str:
        """Show user input prompt"""
        # User message box top
        print(self.color("┌─ You " + "─" * (self.width - 9) + "┐", Colors.BLUE))
        print(self.color("│ ", Colors.BLUE), end="", flush=True)
        
        # Get input
        user_input = input()
        
        # User message box bottom
        print(self.color("└" + "─" * (self.width - 3) + "┘", Colors.BLUE))
        print()
        
        return user_input
    
    def tool_execution(self, tool_name: str, duration: Optional[float] = None):
        """Show tool execution status"""
        if duration is not None:
            print(f"  {self.color('🔧', Colors.YELLOW)} {self.color(tool_name, Colors.BOLD)} {self.color('✓', Colors.GREEN)} {self.color(f'{duration:.2f}s', Colors.DIM)}")
        else:
            print(f"  {self.color('🔧', Colors.YELLOW)} {self.color(tool_name, Colors.BOLD)} {self.color('executing...', Colors.DIM)}", flush=True)
        print()
    
    def assistant_response(self, content: str):
        """Show assistant response"""
        # Assistant message box top
        print(self.color("┌─ Assistant " + "─" * (self.width - 15) + "┐", Colors.GREEN))
        
        # Content (wrap long lines)
        for line in content.split('\n'):
            if len(line) <= self.width - 4:
                # Pad line to fit box width
                padding = self.width - 4 - len(line)
                print(self.color("│ ", Colors.GREEN) + line + " " * padding + self.color("│", Colors.GREEN))
            else:
                # Wrap long lines
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= self.width - 4:
                        current_line += (" " if current_line else "") + word
                    else:
                        padding = self.width - 4 - len(current_line)
                        print(self.color("│ ", Colors.GREEN) + current_line + " " * padding + self.color("│", Colors.GREEN))
                        current_line = word
                if current_line:
                    padding = self.width - 4 - len(current_line)
                    print(self.color("│ ", Colors.GREEN) + current_line + " " * padding + self.color("│", Colors.GREEN))
        
        # Assistant message box bottom
        print(self.color("└" + "─" * (self.width - 3) + "┘", Colors.GREEN))
        print()
    
    def error(self, message: str):
        """Show error message"""
        print(f"{self.color('✗', Colors.RED)} {self.color('Error:', Colors.BOLD + Colors.RED)} {message}")
        print()
    
    def warning(self, message: str):
        """Show warning message"""
        print(f"{self.color('⚠', Colors.YELLOW)} {self.color('Warning:', Colors.BOLD + Colors.YELLOW)} {message}")
        print()
    
    def info(self, message: str):
        """Show info message"""
        print(f"{self.color('ℹ', Colors.BLUE)} {message}")
        print()
    
    def goodbye(self):
        """Show goodbye message"""
        print()
        print(self.color("👋 Goodbye! Thanks for using llmswap MCP.", Colors.CYAN))
        print()
    
    def help_message(self):
        """Show help message"""
        print(self.color("╭─ Available Commands " + "─" * (self.width - 24) + "╮", Colors.CYAN))
        
        # Empty line
        padding = " " * (self.width - 4)
        print(self.color("│", Colors.CYAN) + padding + self.color("│", Colors.CYAN))
        
        commands = [
            ("help", "Show this help message"),
            ("tools", "List all available tools"),
            ("clear", "Clear conversation history"),
            ("status", "Show connection status"),
            ("exit", "Exit the CLI (or use quit, bye)"),
        ]
        
        for cmd, desc in commands:
            cmd_colored = self.color(cmd, Colors.BOLD + Colors.YELLOW)
            # Calculate exact spacing
            content = f"  {cmd}{' ' * (15 - len(cmd))}{desc}"
            padding_right = self.width - 4 - len(content)
            print(f"{self.color('│', Colors.CYAN)}  {cmd_colored}{' ' * (15 - len(cmd))}{desc}{' ' * padding_right}{self.color('│', Colors.CYAN)}")
        
        # Empty line
        padding = " " * (self.width - 4)
        print(self.color("│", Colors.CYAN) + padding + self.color("│", Colors.CYAN))
        print(self.color("╰" + "─" * (self.width - 3) + "╯", Colors.CYAN))
        print()
    
    def tools_list(self, tools: list):
        """Show available tools"""
        print(self.color("╭─ Available Tools " + "─" * (self.width - 21) + "╮", Colors.CYAN))
        
        # Empty line
        padding = " " * (self.width - 4)
        print(self.color("│", Colors.CYAN) + padding + self.color("│", Colors.CYAN))
        
        if not tools:
            content = "  No tools available"
            padding_right = self.width - 4 - len(content)
            print(f"{self.color('│', Colors.CYAN)}{content}{' ' * padding_right}{self.color('│', Colors.CYAN)}")
        else:
            for tool in tools:
                name = tool.get('name', 'unknown')
                desc = tool.get('description', 'No description')
                
                # Truncate description if too long
                max_desc_len = self.width - 10
                if len(desc) > max_desc_len:
                    desc = desc[:max_desc_len - 3] + "..."
                
                # Tool name line
                content = f"  • {name}"
                padding_right = self.width - 4 - len(content)
                print(f"{self.color('│', Colors.CYAN)}  {self.color('•', Colors.YELLOW)} {self.color(name, Colors.BOLD)}{' ' * (padding_right - 2)}{self.color('│', Colors.CYAN)}")
                
                # Description line
                content_desc = f"    {desc}"
                padding_right = self.width - 4 - len(content_desc)
                print(f"{self.color('│', Colors.CYAN)}    {self.color(desc, Colors.DIM)}{' ' * padding_right}{self.color('│', Colors.CYAN)}")
                
                # Empty line between tools (except last)
                if tool != tools[-1]:
                    padding = " " * (self.width - 4)
                    print(self.color("│", Colors.CYAN) + padding + self.color("│", Colors.CYAN))
        
        # Empty line
        padding = " " * (self.width - 4)
        print(self.color("│", Colors.CYAN) + padding + self.color("│", Colors.CYAN))
        print(self.color("╰" + "─" * (self.width - 3) + "╯", Colors.CYAN))
        print()
    
    def thinking(self, message: str = "Thinking"):
        """Show thinking animation (simple version)"""
        print(f"{self.color('⚙', Colors.CYAN)} {self.color(message, Colors.DIM)}...", end="", flush=True)
    
    def thinking_done(self):
        """Clear thinking message"""
        print("\r" + " " * 50 + "\r", end="", flush=True)


class SimpleUI:
    """Fallback simple UI without colors"""
    
    def __init__(self, width: int = 70):
        self.width = width
    
    def color(self, text: str, color: str) -> str:
        return text
    
    def header(self, provider: str, model: Optional[str] = None):
        print("=" * self.width)
        print(f"  llmswap MCP Client - {provider}")
        print("  Natural language interface • Type 'help' for commands")
        print("=" * self.width)
        print()
    
    def connection_status(self, server_type: str, tools_count: int, tools_names: list = None):
        print(f"✓ Connected to {server_type} MCP server")
        print(f"✓ {tools_count} tools available")
        print()
    
    def user_prompt(self) -> str:
        user_input = input("You: ").strip()
        print()
        return user_input
    
    def tool_execution(self, tool_name: str, duration: Optional[float] = None):
        if duration:
            print(f"  🔧 {tool_name} ✓ ({duration:.2f}s)")
        else:
            print(f"  🔧 {tool_name} executing...", flush=True)
    
    def assistant_response(self, content: str):
        print("Assistant:")
        for line in content.split('\n'):
            print(f"  {line}")
        print()
    
    def error(self, message: str):
        print(f"✗ Error: {message}")
        print()
    
    def warning(self, message: str):
        print(f"⚠ Warning: {message}")
        print()
    
    def info(self, message: str):
        print(f"ℹ {message}")
        print()
    
    def goodbye(self):
        print()
        print("👋 Goodbye!")
        print()
    
    def help_message(self):
        print("Available Commands:")
        print("  help   - Show this help message")
        print("  tools  - List all available tools")
        print("  clear  - Clear conversation history")
        print("  status - Show connection status")
        print("  exit   - Exit the CLI")
        print()
    
    def tools_list(self, tools: list):
        print("Available Tools:")
        for tool in tools:
            name = tool.get('name', 'unknown')
            desc = tool.get('description', 'No description')
            print(f"  • {name}: {desc}")
        print()
    
    def thinking(self, message: str = "Thinking"):
        print(f"⚙ {message}...", end="", flush=True)
    
    def thinking_done(self):
        print("\r" + " " * 50 + "\r", end="", flush=True)
