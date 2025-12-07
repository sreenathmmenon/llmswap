"""
Tool schema definition for universal tool calling across LLM providers.

This module provides the Tool class for defining tools/functions that can be
used with any LLM provider (Anthropic, OpenAI, Gemini, etc.).
"""

from typing import Dict, List, Any, Optional


class Tool:
    """
    Universal tool definition that works across all LLM providers.

    A Tool represents a function that an LLM can call during conversation.
    The tool definition is provider-agnostic - format conversion happens automatically.

    Example:
        calculator = Tool(
            name="calculate",
            description="Perform mathematical calculations",
            parameters={
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate"
                }
            },
            required=["expression"]
        )
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required: Optional[List[str]] = None,
    ):
        """
        Initialize a Tool definition.

        Args:
            name: Tool name (must be alphanumeric with underscores)
            description: Clear description of what the tool does
            parameters: Dictionary of parameter definitions (JSON Schema format)
            required: List of required parameter names

        Raises:
            ValueError: If name is invalid or parameters are malformed
        """
        # Validate name
        if not name:
            raise ValueError("Tool name cannot be empty")
        if not name.replace("_", "").isalnum():
            raise ValueError(
                f"Tool name '{name}' must be alphanumeric with underscores only"
            )

        # Validate description
        if not description or not description.strip():
            raise ValueError("Tool description cannot be empty")

        # Validate parameters
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a dictionary")

        # Validate required list
        if required is not None:
            if not isinstance(required, list):
                raise ValueError("Required must be a list of parameter names")
            for req_param in required:
                if req_param not in parameters:
                    raise ValueError(
                        f"Required parameter '{req_param}' not found in parameters"
                    )

        self.name = name
        self.description = description.strip()
        self.parameters = parameters
        self.required = required if required is not None else []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool to dictionary format (base format for conversion).

        Returns:
            Dictionary representation of the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "required": self.required,
        }

    def to_anthropic_format(self) -> Dict[str, Any]:
        """
        Convert to Anthropic tool format.

        Anthropic uses a direct format with input_schema.

        Returns:
            Tool in Anthropic format
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required,
            },
        }

    def to_openai_format(self) -> Dict[str, Any]:
        """
        Convert to OpenAI tool format.

        OpenAI wraps tools in a function object with type.

        Returns:
            Tool in OpenAI format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }

    def to_gemini_format(self) -> Dict[str, Any]:
        """
        Convert to Gemini tool format.

        Gemini uses FunctionDeclaration with specific type mappings.

        Returns:
            Tool in Gemini format
        """
        # Gemini requires type conversion for parameters
        gemini_properties = {}
        for param_name, param_def in self.parameters.items():
            gemini_param = {
                "type_": param_def.get("type", "string").upper(),
                "description": param_def.get("description", ""),
            }
            gemini_properties[param_name] = gemini_param

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type_": "OBJECT",
                "properties": gemini_properties,
                "required": self.required,
            },
        }

    def __repr__(self) -> str:
        """String representation of the tool."""
        return f"Tool(name='{self.name}', parameters={list(self.parameters.keys())})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name}: {self.description}"
