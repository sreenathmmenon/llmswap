"""
Provider verification module for llmswap v5.1.8

Adds real health check functionality to verify API keys and provider availability.
"""

import os
import time
import concurrent.futures
from typing import Dict, List, Optional, Any
from .client import LLMClient
from .exceptions import ProviderError, ConfigurationError


def verify_provider(provider_name: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Verify a single provider with real API call.

    Args:
        provider_name: Name of provider to verify
        timeout: Timeout in seconds for verification

    Returns:
        Dictionary with verification results:
        {
            'name': str,
            'status': str,  # 'verified', 'invalid_key', 'not_configured', 'error', 'slow'
            'api_key_configured': bool,
            'api_key_valid': bool,
            'latency_ms': int or None,
            'model': str or None,
            'error': dict or None
        }
    """
    result = {
        "name": provider_name,
        "status": "unknown",
        "api_key_configured": False,
        "api_key_valid": False,
        "latency_ms": None,
        "model": None,
        "error": None,
    }

    # Check API key configuration first
    api_key_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "groq": "GROQ_API_KEY",
        "cohere": "COHERE_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY",
        "watsonx": "WATSONX_API_KEY",
        "xai": "XAI_API_KEY",
        "sarvam": "SARVAM_API_KEY",
    }

    # Special case for Ollama (local, no API key)
    if provider_name == "ollama":
        return verify_ollama(timeout)

    # Check if API key is configured
    env_key = api_key_map.get(provider_name)
    if not env_key or not os.getenv(env_key):
        result["status"] = "not_configured"
        result["error"] = {
            "type": "ConfigurationError",
            "message": f"{env_key} not set",
        }
        return result

    result["api_key_configured"] = True

    # WatsonX needs both API key and project ID
    if provider_name == "watsonx":
        if not os.getenv("WATSONX_PROJECT_ID"):
            result["status"] = "not_configured"
            result["error"] = {
                "type": "ConfigurationError",
                "message": "WATSONX_PROJECT_ID not set",
            }
            return result

    # Verify with real API call
    try:
        client = LLMClient(provider=provider_name, cache_enabled=False)

        # Minimal test query (costs ~$0.00001)
        test_query = "Say 'OK'"

        start_time = time.time()
        response = client.query(test_query, timeout=timeout)
        latency = int((time.time() - start_time) * 1000)  # Convert to ms

        result["latency_ms"] = latency
        result["api_key_valid"] = True
        result["model"] = getattr(response, "model", None)

        # Check if response is slow
        if latency > 1000:
            result["status"] = "slow"
            result["error"] = {
                "type": "PerformanceWarning",
                "message": f"Response time {latency}ms exceeds 1000ms threshold",
            }
        else:
            result["status"] = "verified"

    except ConfigurationError as e:
        result["status"] = "invalid_key"
        result["error"] = {
            "type": "AuthenticationError",
            "code": 401,
            "message": str(e),
        }
    except ProviderError as e:
        error_str = str(e).lower()

        # Detect specific error types
        if "401" in error_str or "unauthorized" in error_str or "invalid" in error_str:
            result["status"] = "invalid_key"
            result["error"] = {
                "type": "AuthenticationError",
                "code": 401,
                "message": "Invalid API key",
            }
        elif "429" in error_str or "rate limit" in error_str:
            result["status"] = "rate_limited"
            result["error"] = {
                "type": "RateLimitError",
                "code": 429,
                "message": "Rate limit exceeded",
            }
        elif "timeout" in error_str:
            result["status"] = "error"
            result["error"] = {"type": "TimeoutError", "message": "Request timeout"}
        else:
            result["status"] = "error"
            result["error"] = {"type": "ProviderError", "message": str(e)}
    except Exception as e:
        result["status"] = "error"
        result["error"] = {"type": "UnknownError", "message": str(e)}

    return result


def verify_ollama(timeout: int = 5) -> Dict[str, Any]:
    """Verify Ollama local server."""
    result = {
        "name": "ollama",
        "status": "unknown",
        "api_key_configured": True,  # Local, no key needed
        "api_key_valid": True,
        "latency_ms": None,
        "model": "local",
        "error": None,
    }

    try:
        import requests

        start_time = time.time()
        response = requests.get("http://localhost:11434/api/tags", timeout=timeout)
        latency = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            result["status"] = "verified"
            result["latency_ms"] = latency
        else:
            result["status"] = "not_running"
            result["error"] = {
                "type": "ServiceError",
                "message": f"Server returned {response.status_code}",
            }
    except requests.exceptions.Timeout:
        result["status"] = "not_running"
        result["error"] = {
            "type": "TimeoutError",
            "message": "Local server not responding",
        }
    except Exception as e:
        result["status"] = "not_running"
        result["error"] = {
            "type": "ServiceError",
            "message": f"Server not running: {str(e)}",
        }

    return result


def verify_all_providers(
    provider_filter: Optional[str] = None, timeout: int = 10, concurrent: bool = True
) -> Dict[str, Any]:
    """
    Verify all providers or filtered subset.

    Args:
        provider_filter: Optional provider name to verify only one
        timeout: Timeout per provider in seconds
        concurrent: Whether to verify concurrently (faster)

    Returns:
        Dictionary with verification results and summary
    """
    from .config import get_config

    config = get_config()
    all_providers = config.get("provider.fallback_order", [])

    # Filter to specific provider if requested
    if provider_filter:
        if provider_filter.lower() in all_providers:
            providers_to_check = [provider_filter.lower()]
        else:
            return {
                "error": f"Provider '{provider_filter}' not found",
                "available_providers": all_providers,
            }
    else:
        providers_to_check = all_providers

    # Verify providers
    if concurrent and len(providers_to_check) > 1:
        # Parallel verification for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_provider = {
                executor.submit(verify_provider, provider, timeout): provider
                for provider in providers_to_check
            }

            results = []
            for future in concurrent.futures.as_completed(future_to_provider):
                results.append(future.result())
    else:
        # Sequential verification
        results = [
            verify_provider(provider, timeout) for provider in providers_to_check
        ]

    # Calculate summary
    summary = {
        "total": len(results),
        "verified": sum(1 for r in results if r["status"] == "verified"),
        "invalid": sum(1 for r in results if r["status"] == "invalid_key"),
        "not_configured": sum(1 for r in results if r["status"] == "not_configured"),
        "slow": sum(1 for r in results if r["status"] == "slow"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "not_running": sum(1 for r in results if r["status"] == "not_running"),
    }

    # Generate recommendations
    recommendations = []

    for r in results:
        if r["status"] == "invalid_key":
            recommendations.append(
                {
                    "provider": r["name"],
                    "issue": "invalid_key",
                    "action": f"Check {r['name'].upper()}_API_KEY environment variable",
                }
            )
        elif r["status"] == "not_configured":
            env_key = r["error"]["message"].split()[0]
            recommendations.append(
                {
                    "provider": r["name"],
                    "issue": "not_configured",
                    "action": f"Set {env_key} environment variable",
                }
            )
        elif r["status"] == "slow":
            recommendations.append(
                {
                    "provider": r["name"],
                    "issue": "slow_response",
                    "action": f"Consider using faster provider ({r['latency_ms']}ms is slow)",
                }
            )
        elif r["status"] == "not_running":
            if r["name"] == "ollama":
                recommendations.append(
                    {
                        "provider": r["name"],
                        "issue": "not_running",
                        "action": "Run 'ollama serve' to start local server",
                    }
                )

    # Find fastest and cheapest verified providers
    verified = [
        r for r in results if r["status"] in ["verified", "slow"] and r["latency_ms"]
    ]
    if verified:
        fastest = min(verified, key=lambda x: x["latency_ms"])
        # Cheap providers (rough estimate based on typical costs)
        cheap_providers = ["groq", "gemini", "ollama"]
        cheapest = [r for r in verified if r["name"] in cheap_providers]
    else:
        fastest = None
        cheapest = []

    return {
        "providers": results,
        "summary": summary,
        "recommendations": recommendations,
        "fastest": fastest,
        "cheapest": cheapest if cheapest else None,
    }
