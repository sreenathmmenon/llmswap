"""
Response handling for tool calling across LLM providers.

This module provides universal response objects for tool calls,
extracting and normalizing tool call data from different providers.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolCall:
    """
    Universal tool call representation.

    Represents a tool/function call request from an LLM, normalized
    across all providers.

    Attributes:
        id: Unique identifier for this tool call
        name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
    """

    id: str
    name: str
    arguments: Dict[str, Any]

    def __repr__(self) -> str:
        """String representation."""
        args_preview = str(self.arguments)[:50]
        if len(str(self.arguments)) > 50:
            args_preview += "..."
        return f"ToolCall(id='{self.id}', name='{self.name}', args={args_preview})"


class EnhancedResponse:
    """
    Enhanced response object that includes tool calling information.

    This wraps the standard LLM response and adds normalized tool call data.

    Attributes:
        content: Text response from the LLM
        tool_calls: List of ToolCall objects (if LLM wants to use tools)
        finish_reason: Why generation stopped
        raw_response: Original provider response
        provider: Name of the provider used
    """

    def __init__(
        self,
        content: str,
        tool_calls: Optional[List[ToolCall]] = None,
        finish_reason: Optional[str] = None,
        raw_response: Any = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize enhanced response.

        Args:
            content: Text response content
            tool_calls: List of tool calls (if any)
            finish_reason: Reason generation stopped
            raw_response: Original provider response object
            provider: Provider name
        """
        self.content = content
        self.tool_calls = tool_calls if tool_calls is not None else []
        self.finish_reason = finish_reason
        self.raw_response = raw_response
        self.provider = provider

    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return len(self.tool_calls) > 0

    def get_tool_call(self, name: str) -> Optional[ToolCall]:
        """
        Get first tool call with given name.

        Args:
            name: Tool name to find

        Returns:
            ToolCall object or None if not found
        """
        for tool_call in self.tool_calls:
            if tool_call.name == name:
                return tool_call
        return None

    def __repr__(self) -> str:
        """String representation."""
        tool_info = f", {len(self.tool_calls)} tool_calls" if self.tool_calls else ""
        content_preview = self.content[:50]
        if len(self.content) > 50:
            content_preview += "..."
        return f"EnhancedResponse(content='{content_preview}'{tool_info}, provider='{self.provider}')"


def extract_anthropic_tool_calls(response: Any) -> List[ToolCall]:
    """
    Extract tool calls from Anthropic response.

    Anthropic returns tool_use blocks in the response content.

    Args:
        response: Anthropic API response object

    Returns:
        List of ToolCall objects
    """
    tool_calls = []

    if not hasattr(response, "content"):
        return tool_calls

    for block in response.content:
        if hasattr(block, "type") and block.type == "tool_use":
            tool_calls.append(
                ToolCall(id=block.id, name=block.name, arguments=block.input)
            )

    return tool_calls


def extract_openai_tool_calls(response: Any) -> List[ToolCall]:
    """
    Extract tool calls from OpenAI response.

    OpenAI returns tool_calls in the message object.

    Args:
        response: OpenAI API response object

    Returns:
        List of ToolCall objects
    """
    tool_calls = []

    if not hasattr(response, "choices") or not response.choices:
        return tool_calls

    message = response.choices[0].message

    if hasattr(message, "tool_calls") and message.tool_calls:
        import json

        for tc in message.tool_calls:
            # OpenAI returns arguments as JSON string
            args = (
                json.loads(tc.function.arguments)
                if isinstance(tc.function.arguments, str)
                else tc.function.arguments
            )
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))

    return tool_calls


def extract_gemini_tool_calls(response: Any) -> List[ToolCall]:
    """
    Extract tool calls from Gemini response.

    Gemini returns function_calls in the parts of the response.

    Args:
        response: Gemini API response object

    Returns:
        List of ToolCall objects
    """
    tool_calls = []

    if not hasattr(response, "candidates") or not response.candidates:
        return tool_calls

    for candidate in response.candidates:
        if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
            for part in candidate.content.parts:
                if hasattr(part, "function_call"):
                    func_call = part.function_call

                    # Skip empty function calls (Gemini sometimes returns these)
                    if not hasattr(func_call, "name") or not func_call.name:
                        continue

                    # Convert Gemini's protobuf args to dict
                    args = {}
                    if hasattr(func_call, "args") and func_call.args:
                        try:
                            for key, value in func_call.args.items():
                                args[key] = value
                        except:
                            # If iteration fails, just use empty args
                            pass

                    tool_calls.append(
                        ToolCall(
                            id=func_call.name,  # Gemini doesn't have separate ID
                            name=func_call.name,
                            arguments=args,
                        )
                    )

    return tool_calls


def create_enhanced_response(response: Any, provider: str) -> EnhancedResponse:
    """
    Create enhanced response from provider response.

    Args:
        response: Provider-specific response object
        provider: Provider name ("anthropic", "openai", "groq")

    Returns:
        EnhancedResponse object with normalized tool calls
    """
    provider_lower = provider.lower()

    # Extract content based on provider
    if provider_lower == "anthropic":
        content = ""
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                content += block.text
        tool_calls = extract_anthropic_tool_calls(response)
        finish_reason = response.stop_reason

    elif provider_lower in ["openai", "groq"]:
        message = response.choices[0].message
        content = message.content if message.content else ""
        tool_calls = extract_openai_tool_calls(response)
        finish_reason = response.choices[0].finish_reason

    elif provider_lower == "gemini":
        content = ""
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        content += part.text
        tool_calls = extract_gemini_tool_calls(response)
        finish_reason = (
            getattr(response.candidates[0], "finish_reason", None)
            if hasattr(response, "candidates") and response.candidates
            else None
        )

    else:
        # Fallback for unknown providers
        content = str(response)
        tool_calls = []
        finish_reason = None

    return EnhancedResponse(
        content=content,
        tool_calls=tool_calls,
        finish_reason=finish_reason,
        raw_response=response,
        provider=provider,
    )
