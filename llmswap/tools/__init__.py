"""
Universal tool calling support for llmswap.

This module provides tool/function calling capabilities that work across
all LLM providers.
"""

from .schema import Tool
from .response import ToolCall, EnhancedResponse, create_enhanced_response

__all__ = ["Tool", "ToolCall", "EnhancedResponse", "create_enhanced_response"]
