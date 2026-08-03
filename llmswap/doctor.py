"""Installation and provider-readiness diagnostics for LLMSwap."""

import importlib.util
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from . import __version__
from .config import get_config
from .provider_registry import PROVIDER_SPECS, get_provider_names

PROVIDER_MODULES = {
    "anthropic": "anthropic",
    "openai": "openai",
    "gemini": "google.genai",
    "cohere": "cohere",
    "perplexity": "openai",
    "watsonx": "ibm_watsonx_ai",
    "groq": "groq",
    "ollama": "requests",
    "xai": "openai",
    "sarvam": "requests",
}


def _load_env_files() -> List[str]:
    """Load conventional env files without overriding exported variables."""
    loaded = []
    candidates = [Path.cwd() / ".env", Path.home() / ".env"]
    for env_file in dict.fromkeys(candidates):
        if env_file.is_file():
            load_dotenv(env_file, override=False)
            loaded.append(str(env_file))
    return loaded


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def diagnose(
    live: bool = False,
    provider: Optional[str] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """Collect a secret-safe LLMSwap readiness report."""
    env_files = _load_env_files()
    config = get_config()
    config_issues = config.validate()
    configured_models = config.get("provider.models", {}) or {}
    invoked_path = Path(sys.argv[0])
    if invoked_path.name == "llmswap":
        cli_path = str(invoked_path.absolute())
    else:
        cli_path = shutil.which("llmswap")
    # Resolve the environment directories, not the executable files: venv
    # Python is commonly a symlink to the base interpreter.
    executable_dir = Path(sys.executable).parent.resolve()
    cli_matches_python = bool(
        cli_path and Path(cli_path).parent.resolve() == executable_dir
    )

    provider_names = get_provider_names()
    selected_names = [provider] if provider else provider_names
    providers = []
    recommendations = []

    for name in selected_names:
        spec = PROVIDER_SPECS[name]
        required_env = [spec.env_key] if spec.env_key else []
        if name == "watsonx":
            required_env.append("WATSONX_PROJECT_ID")
        missing_env = [key for key in required_env if not os.getenv(key)]
        package_name = PROVIDER_MODULES[name]
        package_installed = _module_available(package_name)
        configured = not missing_env if required_env else None
        if name == "ollama":
            status = "live_check_required" if package_installed else "sdk_missing"
        elif missing_env:
            status = "not_configured"
        elif not package_installed:
            status = "sdk_missing"
        else:
            status = "ready"

        provider_result = {
            "name": name,
            "model": configured_models.get(name, spec.default_model),
            "credential_env": required_env,
            "missing_env": missing_env,
            "credentials_configured": configured,
            "sdk_module": package_name,
            "sdk_installed": package_installed,
            "status": status,
        }
        providers.append(provider_result)

        if missing_env and provider:
            recommendations.append(f"Set {', '.join(missing_env)} to use {name}.")
        if not package_installed and (provider or configured):
            install_target = "llmswap[watsonx]" if name == "watsonx" else "llmswap"
            recommendations.append(
                f"Install {install_target} to add the {name} runtime dependency."
            )

    live_results = []
    if live:
        from .verification import verify_provider

        live_names = (
            selected_names
            if provider
            else [item["name"] for item in providers if item["credentials_configured"]]
        )
        for name in live_names:
            result = verify_provider(name, timeout=timeout)
            live_results.append(result)
            for item in providers:
                if item["name"] == name:
                    item["status"] = result["status"]
                    break

    python_supported = sys.version_info >= (3, 9)
    npx_path = shutil.which("npx")
    configured_cloud_count = sum(
        item["credentials_configured"] is True for item in providers
    )

    if not cli_path:
        recommendations.append(
            f"Run {sys.executable} -m pip install llmswap to install the CLI."
        )
    elif not cli_matches_python:
        recommendations.append(
            "The llmswap CLI and current Python come from different environments. "
            f"Use {sys.executable} -m llmswap.app or reinstall LLMSwap in this Python."
        )
    if not npx_path:
        recommendations.append("Install Node.js/npm to use local MCP servers via npx.")
    if not provider and configured_cloud_count == 0:
        recommendations.append(
            "Configure a provider key, for example OPENAI_API_KEY, or run Ollama locally."
        )
    for issue in config_issues:
        recommendations.append(f"Fix configuration: {issue}")

    fatal = not python_supported or bool(config_issues)
    if provider:
        selected = providers[0]
        fatal = fatal or selected["status"] in {
            "not_configured",
            "sdk_missing",
            "invalid_key",
            "error",
            "not_running",
        }
    elif live:
        fatal = fatal or any(
            result["status"] not in {"verified", "slow", "rate_limited"}
            for result in live_results
        )

    return {
        "healthy": not fatal,
        "llmswap_version": __version__,
        "python": {
            "version": ".".join(map(str, sys.version_info[:3])),
            "executable": sys.executable,
            "supported": python_supported,
        },
        "installation": {
            "module_path": str(Path(__file__).resolve().parent),
            "cli_path": cli_path,
            "cli_matches_python": cli_matches_python,
        },
        "environment": {
            "loaded_files": env_files,
            "secret_values_exposed": False,
        },
        "configuration": {
            "path": str(config.config_path),
            "valid": not config_issues,
            "issues": config_issues,
        },
        "mcp": {
            "npx_available": bool(npx_path),
            "npx_path": npx_path,
        },
        "providers": providers,
        "live_verification": live_results,
        "recommendations": list(dict.fromkeys(recommendations)),
    }
