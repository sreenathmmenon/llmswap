"""
LLMSwap Web UI - Workspace Integration

Handles saving comparison results to workspace journals and managing workspace data.

Copyright (c) 2025 Sreenath M Menon
Licensed under the MIT License
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def save_comparison(workspace, data: Dict[str, Any]) -> Optional[str]:
    """
    Save comparison results to workspace journal.

    Args:
        workspace: Workspace instance or None
        data: Comparison data with prompt, results

    Returns:
        Path to saved entry or None
    """
    if workspace is None:
        return None

    try:
        # Format the comparison entry
        entry = format_comparison_entry(data)

        # Log to workspace (if workspace has log_interaction method)
        if hasattr(workspace, "log_interaction"):
            workspace.log_interaction(
                prompt=data.get("prompt", ""),
                response=entry,
                model="multi-model-comparison",
                cost=sum(r.get("cost", 0) for r in data.get("results", [])),
            )

        return str(workspace.path / "workspace-journal.md")
    except Exception as e:
        print(f"Error saving comparison: {e}")
        return None


def format_comparison_entry(data: Dict[str, Any]) -> str:
    """
    Format comparison results as markdown entry.

    Args:
        data: Comparison data

    Returns:
        Formatted markdown string
    """
    prompt = data.get("prompt", "")
    results = data.get("results", [])
    timestamp = data.get("timestamp", datetime.now().isoformat())

    lines = [
        f"## Model Comparison - {timestamp}",
        "",
        f"**Prompt:** {prompt}",
        "",
        "### Results",
        "",
    ]

    for result in results:
        model = result.get("model", "unknown")
        response = result.get("response", "")
        time_taken = result.get("time", 0)
        tokens = result.get("tokens", 0)
        cost = result.get("cost", 0)
        error = result.get("error")

        lines.append(f"#### {model}")
        lines.append("")

        if error:
            lines.append(f"**Error:** {error}")
        else:
            lines.append(f"**Response:** {response}")
            lines.append("")
            lines.append(f"- Time: {time_taken}s")
            lines.append(f"- Tokens: {tokens}")
            lines.append(f"- Cost: ${cost:.4f}")

        lines.append("")

    # Total stats
    total_cost = sum(r.get("cost", 0) for r in results if not r.get("error"))
    total_time = sum(r.get("time", 0) for r in results if not r.get("error"))

    lines.append("### Summary")
    lines.append("")
    lines.append(f"- Models compared: {len(results)}")
    lines.append(f"- Total cost: ${total_cost:.4f}")
    lines.append(f"- Total time: {total_time:.2f}s")

    return "\n".join(lines)


def get_workspace(name: str):
    """
    Get workspace by name.

    Args:
        name: Workspace name

    Returns:
        Workspace instance
    """
    try:
        from llmswap.workspace import Workspace

        return Workspace(name)
    except Exception:
        return None


def get_or_create_workspace(name: str):
    """
    Get existing workspace or create new one.

    Args:
        name: Workspace name

    Returns:
        Workspace instance
    """
    try:
        from llmswap.workspace import Workspace

        ws = Workspace(name)
        return ws
    except Exception:
        # If error, try creating
        try:
            from llmswap.workspace import Workspace

            ws = Workspace(name)
            # Initialize if needed
            return ws
        except Exception:
            return None


def list_workspaces() -> List[str]:
    """
    List all available workspaces.

    Returns:
        List of workspace names
    """
    try:
        from llmswap.workspace import Workspace

        if hasattr(Workspace, "list_all"):
            return Workspace.list_all()
        else:
            # Fallback: scan workspace directory
            workspace_dir = Path.home() / ".llmswap" / "workspaces"
            if workspace_dir.exists():
                return [d.name for d in workspace_dir.iterdir() if d.is_dir()]
            return []
    except Exception:
        return []


def get_workspace_stats(workspace) -> Dict[str, Any]:
    """
    Get statistics for a workspace.

    Args:
        workspace: Workspace instance

    Returns:
        Dict with stats
    """
    try:
        if hasattr(workspace, "get_stats"):
            return workspace.get_stats()
        else:
            # Fallback stats
            return {"total_queries": 0, "total_cost": 0.0, "comparisons": 0}
    except Exception:
        return {"total_queries": 0, "total_cost": 0.0, "comparisons": 0}


def get_comparison_history(workspace) -> List[Dict[str, Any]]:
    """
    Get comparison history from workspace.

    Args:
        workspace: Workspace instance

    Returns:
        List of comparison entries
    """
    try:
        if hasattr(workspace, "get_journal"):
            journal = workspace.get_journal()
            # Filter for comparison entries
            return [entry for entry in journal if entry.get("type") == "comparison"]
        return []
    except Exception:
        return []


def export_comparison(data: Dict[str, Any], output_path: str) -> bool:
    """
    Export comparison results to JSON file.

    Args:
        data: Comparison data
        output_path: Path to save file

    Returns:
        True if successful
    """
    try:
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting: {e}")
        return False
