#!/usr/bin/env python3
"""
Simple, Clean UI - Based on Claude Code style
Less is more - focus on usability
"""

import sys
from typing import Optional


class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_CYAN = '\033[96m'


class SimpleCleanUI:
    """Simple, clean UI inspired by Claude Code"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()
        self.separator = "─" * 70
    
    def c(self, text: str, color: str) -> str:
        """Apply color if enabled"""
        if self.use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def header(self, provider: str, model: Optional[str] = None):
        """Clean header"""
        print(self.c(self.separator, Colors.BRIGHT_BLACK))
        title = f"llmswap MCP • {provider}"
        if model:
            title += f" • {model}"
        print(f"{self.c(title, Colors.BOLD + Colors.CYAN)}")
        print(f"{self.c('Type naturally, or', Colors.DIM)} {self.c('help', Colors.YELLOW)} {self.c('for commands', Colors.DIM)}")
        print(self.c(self.separator, Colors.BRIGHT_BLACK))
        print()
    
    def connection_status(self, server_type: str, tools_count: int, tools_names: list = None):
        """Connection info"""
        print(f"{self.c('✓', Colors.GREEN)} Connected • {tools_count} tool{'s' if tools_count != 1 else ''} available")
        print()
    
    def user_prompt(self) -> str:
        """Simple prompt like Claude Code"""
        print(self.c(self.separator, Colors.BRIGHT_BLACK))
        prompt = self.c("> ", Colors.BLUE)
        user_input = input(prompt).strip()
        print()
        return user_input
    
    def tool_execution(self, tool_name: str, duration: Optional[float] = None):
        """Tool indicator"""
        if duration is not None:
            print(f"  {self.c('→', Colors.DIM)} {self.c(tool_name, Colors.YELLOW)} {self.c('✓', Colors.GREEN)} {self.c(f'{duration:.2f}s', Colors.DIM)}")
        else:
            print(f"  {self.c('→', Colors.DIM)} {self.c(tool_name, Colors.YELLOW)} {self.c('...', Colors.DIM)}", flush=True)
        print()
    
    def assistant_response(self, content: str):
        """Simple response"""
        for line in content.split('\n'):
            print(f"  {line}")
        print()
    
    def error(self, message: str):
        """Error message"""
        print(f"{self.c('✗', Colors.RED)} {message}")
        print()
    
    def warning(self, message: str):
        """Warning"""
        print(f"{self.c('⚠', Colors.YELLOW)} {message}")
        print()
    
    def info(self, message: str):
        """Info"""
        print(f"{self.c('ℹ', Colors.BRIGHT_CYAN)} {message}")
        print()
    
    def goodbye(self):
        """Goodbye"""
        print(self.c(self.separator, Colors.BRIGHT_BLACK))
        print(self.c("Thanks for using llmswap MCP!", Colors.CYAN))
        print()
    
    def help_message(self):
        """Help"""
        print(self.c(self.separator, Colors.BRIGHT_BLACK))
        print(self.c("Commands:", Colors.BOLD + Colors.CYAN))
        print()
        commands = [
            ("help", "Show this help"),
            ("tools", "List available tools"),
            ("clear", "Clear history"),
            ("status", "Connection status"),
            ("exit", "Quit (or: quit, bye)"),
        ]
        for cmd, desc in commands:
            print(f"  {self.c(cmd.ljust(10), Colors.YELLOW)} {desc}")
        print()
    
    def tools_list(self, tools: list):
        """Tools list"""
        print(self.c(self.separator, Colors.BRIGHT_BLACK))
        print(self.c("Available Tools:", Colors.BOLD + Colors.CYAN))
        print()
        
        if not tools:
            print(f"  {self.c('No tools available', Colors.DIM)}")
        else:
            for i, tool in enumerate(tools, 1):
                name = tool.get('name', 'unknown')
                desc = tool.get('description', '')
                print(f"  {self.c(f'{i}.', Colors.DIM)} {self.c(name, Colors.BOLD + Colors.YELLOW)}")
                if desc:
                    print(f"     {self.c(desc[:60] + '...' if len(desc) > 60 else desc, Colors.DIM)}")
                if i < len(tools):
                    print()
        print()
    
    def thinking(self, message: str = "Thinking"):
        """Thinking indicator"""
        print(f"{self.c('⚙', Colors.CYAN)} {self.c(message, Colors.DIM)}...", end="", flush=True)
    
    def thinking_done(self):
        """Clear thinking"""
        print("\r" + " " * 60 + "\r", end="", flush=True)


class PlainUI(SimpleCleanUI):
    """Plain version without colors"""
    
    def __init__(self):
        super().__init__(use_colors=False)
