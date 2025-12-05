"""
CLI tools for llmswap
"""

from .mcp_cli import main as mcp_main

# Export main for backwards compatibility
main = mcp_main

__all__ = ["mcp_main", "main"]
