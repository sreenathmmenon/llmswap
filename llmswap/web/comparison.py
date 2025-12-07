"""
LLMSwap Web UI - Model Comparison Logic

Handles concurrent model querying, cost estimation, and result formatting.

Copyright (c) 2025 Sreenath M Menon
Licensed under the MIT License
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any


def compare_models(prompt: str, models: List[str], client=None) -> List[Dict[str, Any]]:
    """
    Compare multiple models with the same prompt concurrently.

    Args:
        prompt: The prompt to send to all models
        models: List of model names to compare
        client: LLMClient instance (optional, creates if not provided)

    Returns:
        List of results with model, response, time, tokens, cost

    Raises:
        ValueError: If prompt is empty or models list is empty
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if not models or len(models) == 0:
        raise ValueError("Models list cannot be empty")

    # Import here to avoid circular dependency
    if client is None:
        from llmswap import LLMClient

        # Disable fallback so we get real errors when API keys are missing
        client = LLMClient(fallback=False)

    results = []

    # Use ThreadPoolExecutor for concurrent queries
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        future_to_model = {
            executor.submit(_query_model, client, model, prompt): model
            for model in models
        }

        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Format user-friendly error message
                error_msg = _format_error_message(model, str(e))
                results.append(
                    {
                        "model": model,
                        "response": None,
                        "error": error_msg,
                        "time": 0,
                        "tokens": 0,
                        "cost": 0,
                    }
                )

    # Sort results by original model order
    model_order = {model: idx for idx, model in enumerate(models)}
    results.sort(key=lambda x: model_order.get(x["model"], 999))

    return results


def _query_model(client, model: str, prompt: str) -> Dict[str, Any]:
    """
    Query a single model and track metrics.

    Args:
        client: LLMClient instance
        model: Model name
        prompt: Prompt text

    Returns:
        Dict with response, timing, tokens, cost
    """
    start_time = time.time()

    try:
        # Detect provider from model name
        provider = _get_provider_for_model(model)

        # Set provider and model explicitly (no fallback)
        client.set_provider(provider)
        client.model = model

        # Query the model
        response = client.query(prompt)

        # Extract text from LLMResponse object
        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)

        # Calculate time
        elapsed = time.time() - start_time

        # Get ACTUAL token counts from API response (if available)
        if hasattr(response, "usage") and response.usage:
            # Use real token counts from API
            prompt_tokens = response.usage.get("prompt_tokens", 0)
            response_tokens = response.usage.get(
                "completion_tokens", 0
            ) or response.usage.get("output_tokens", 0)
            total_tokens = response.usage.get(
                "total_tokens", prompt_tokens + response_tokens
            )
        else:
            # Fallback to estimation (rough: ~4 chars per token)
            prompt_tokens = len(prompt) // 4
            response_tokens = len(response_text) // 4
            total_tokens = prompt_tokens + response_tokens

        # Calculate cost with actual token counts
        cost = _estimate_cost(model, prompt_tokens, response_tokens)

        return {
            "model": model,
            "response": response_text,
            "time": round(elapsed, 2),
            "tokens": total_tokens,
            "cost": round(cost, 4),
        }
    except Exception as e:
        raise


def _format_error_message(model: str, error: str) -> str:
    """
    Format user-friendly error message.

    Args:
        model: Model name
        error: Original error message

    Returns:
        User-friendly error message
    """
    provider = _get_provider_for_model(model)

    # Map providers to setup instructions
    setup_instructions = {
        "openai": 'export OPENAI_API_KEY="your-key-here"',
        "anthropic": 'export ANTHROPIC_API_KEY="your-key-here"',
        "gemini": 'export GEMINI_API_KEY="your-key-here"',
        "xai": 'export XAI_API_KEY="your-key-here"',
        "cohere": 'export COHERE_API_KEY="your-key-here"',
        "perplexity": 'export PERPLEXITY_API_KEY="your-key-here"',
        "watsonx": 'export WATSONX_API_KEY="your-key-here"',
        "groq": 'export GROQ_API_KEY="your-key-here"',
        "ollama": "Make sure Ollama is running: ollama serve",
    }

    # Check for common error patterns
    if "API_KEY" in error or "not found" in error or "missing" in error.lower():
        provider_name = provider.upper() if provider != "xai" else "xAI"
        setup = setup_instructions.get(
            provider, f'export {provider.upper()}_API_KEY="your-key-here"'
        )

        return f"🔑 {provider_name} API key not configured\n\nTo use {model}:\n{setup}\n\nThen restart the web UI."

    elif "rate limit" in error.lower():
        return f"⏱️ Rate limit exceeded for {model}\n\nTry again in a few moments or upgrade your API plan."

    elif "connection" in error.lower() or "timeout" in error.lower():
        return f"🌐 Connection error for {model}\n\nCheck your internet connection and try again."

    elif "not running" in error.lower() or "refused" in error.lower():
        if provider == "ollama":
            return f"🦙 Ollama not running\n\nStart Ollama with: ollama serve\n\nThen try again."
        return f"⚠️ Service unavailable for {model}\n\n{error}"

    else:
        # Generic error with helpful context
        return f"❌ Error with {model}\n\n{error}\n\nCheck your API key and try again."


def _get_provider_for_model(model: str) -> str:
    """
    Detect provider from model name.

    Args:
        model: Model name

    Returns:
        Provider name
    """
    model_lower = model.lower()

    if "gpt" in model_lower or "o1" in model_lower:
        return "openai"
    elif "claude" in model_lower:
        return "anthropic"
    elif "gemini" in model_lower:
        return "gemini"
    elif "grok" in model_lower:
        return "xai"
    elif "command" in model_lower or "cohere" in model_lower:
        return "cohere"
    elif "llama" in model_lower or "mistral" in model_lower:
        return "ollama"
    elif "sonar" in model_lower:
        return "perplexity"
    elif "granite" in model_lower:
        return "watsonx"
    else:
        # Default to openai for unknown models
        return "openai"


def _estimate_cost(model: str, prompt_tokens: int, response_tokens: int) -> float:
    """
    Estimate cost based on model and token counts.

    Uses dynamic pricing from models.py (December 2025 latest).

    Args:
        model: Model ID
        prompt_tokens: Number of input tokens
        response_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    # Try to get pricing from models.py
    try:
        from .models import get_model_pricing

        pricing = get_model_pricing(model)
        input_cost = pricing.get("input", 3.0)
        output_cost = pricing.get("output", 15.0)
    except:
        # Fallback to default pricing
        input_cost, output_cost = (3.0, 15.0)

    # Calculate cost (pricing is per 1M tokens)
    cost = (prompt_tokens * input_cost + response_tokens * output_cost) / 1_000_000

    return cost


def compare_models_streaming(prompt: str, models: List[str], client=None):
    """
    Compare models with REAL-TIME streaming (side-by-side).

    Yields token-by-token updates as models generate responses.
    This enables LIVE side-by-side comparison in the UI.

    Yields:
        Dict with: model, chunk, done, time, tokens, cost
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if not models or len(models) == 0:
        raise ValueError("Models list cannot be empty")

    if client is None:
        from llmswap import LLMClient

        client = LLMClient()

    # Track per-model state
    model_states = {
        model: {"chunks": [], "start_time": None, "tokens": 0, "done": False}
        for model in models
    }

    def stream_single_model(model: str):
        """Stream a single model and yield chunks."""
        try:
            provider = _get_provider_for_model(model)
            client.set_provider(provider)
            client.model = model

            model_states[model]["start_time"] = time.time()

            # Stream from provider
            for chunk in client.stream(prompt):
                # Extract text from chunk
                if hasattr(chunk, "content"):
                    text = chunk.content
                elif isinstance(chunk, str):
                    text = chunk
                else:
                    text = str(chunk)

                model_states[model]["chunks"].append(text)
                model_states[model]["tokens"] = (
                    len("".join(model_states[model]["chunks"])) // 4
                )

                yield {
                    "model": model,
                    "chunk": text,
                    "done": False,
                    "time": round(time.time() - model_states[model]["start_time"], 2),
                    "tokens": model_states[model]["tokens"],
                    "cost": 0,  # Calculate at end
                }

            # Final summary
            full_response = "".join(model_states[model]["chunks"])
            elapsed = time.time() - model_states[model]["start_time"]
            total_tokens = len(full_response) // 4
            prompt_tokens = len(prompt) // 4
            cost = _estimate_cost(model, prompt_tokens, total_tokens - prompt_tokens)

            model_states[model]["done"] = True

            yield {
                "model": model,
                "chunk": "",
                "done": True,
                "time": round(elapsed, 2),
                "tokens": total_tokens,
                "tokens_per_sec": (
                    round(total_tokens / elapsed, 1) if elapsed > 0 else 0
                ),
                "cost": round(cost, 4),
                "full_response": full_response,
            }

        except Exception as e:
            yield {
                "model": model,
                "chunk": "",
                "done": True,
                "error": _format_error_message(model, str(e)),
                "time": 0,
                "tokens": 0,
                "cost": 0,
            }

    # Use ThreadPoolExecutor for concurrent streaming
    import queue

    q = queue.Queue()

    def worker(model):
        for update in stream_single_model(model):
            q.put(update)

    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        # Start all streams
        futures = [executor.submit(worker, model) for model in models]

        # Yield updates as they arrive
        completed = 0
        while completed < len(models):
            try:
                update = q.get(timeout=0.1)
                yield update

                if update.get("done"):
                    completed += 1

            except queue.Empty:
                continue

        # Wait for all to complete
        for future in futures:
            future.result()


def detect_winner(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Automatically detect the "winner" from comparison results.

    Scoring algorithm:
    - Quality (40%): Response length, structure
    - Speed (30%): Tokens per second
    - Cost (20%): Lower is better
    - Completeness (10%): Error-free response

    Args:
        results: List of comparison results

    Returns:
        Dict with winner, runner_up, reasoning
    """
    if not results:
        return {"winner": None, "reasoning": "No results to compare"}

    # Filter out errors
    valid_results = [r for r in results if not r.get("error")]

    if not valid_results:
        return {"winner": None, "reasoning": "All models failed"}

    # Score each result
    scored = []

    for result in valid_results:
        # Quality score (0-10): Based on response length and token count
        tokens = result.get("tokens", 0)
        quality = min(10, tokens / 100)  # 1000 tokens = 10/10

        # Speed score (0-10): Tokens per second (higher is better)
        time_sec = result.get("time", 1)
        if time_sec > 0:
            tokens_per_sec = tokens / time_sec
            speed = min(10, tokens_per_sec / 10)  # 100 tok/sec = 10/10
        else:
            speed = 0

        # Cost score (0-10): Lower cost is better
        cost = result.get("cost", 0)
        if cost == 0:  # Free (Ollama)
            cost_score = 10
        else:
            cost_score = max(0, 10 - (cost * 1000))  # $0.01 = 0/10

        # Completeness score (0-10): No errors = 10
        completeness = 10 if not result.get("error") else 0

        # Weighted total score
        total_score = (
            quality * 0.4 + speed * 0.3 + cost_score * 0.2 + completeness * 0.1
        )

        scored.append(
            {
                "result": result,
                "score": total_score,
                "quality": quality,
                "speed": speed,
                "cost_score": cost_score,
            }
        )

    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)

    winner = scored[0]
    runner_up = scored[1] if len(scored) > 1 else None

    # Generate reasoning
    reasons = []
    if winner["quality"] > 7:
        reasons.append(f"high quality response ({winner['result']['tokens']} tokens)")
    if winner["speed"] > 7:
        tokens_per_sec = (
            winner["result"]["tokens"] / winner["result"]["time"]
            if winner["result"]["time"] > 0
            else 0
        )
        reasons.append(f"fast generation ({round(tokens_per_sec, 1)} tok/s)")
    if winner["cost_score"] > 7:
        if winner["result"]["cost"] == 0:
            reasons.append("free (local model)")
        else:
            reasons.append(f"low cost (${winner['result']['cost']:.4f})")

    reasoning = "Best " + ", ".join(reasons) if reasons else "Highest overall score"

    return {
        "winner": winner["result"]["model"],
        "winner_score": round(winner["score"], 1),
        "runner_up": runner_up["result"]["model"] if runner_up else None,
        "reasoning": reasoning,
        "all_scores": {
            r["result"]["model"]: {
                "total": round(r["score"], 1),
                "quality": round(r["quality"], 1),
                "speed": round(r["speed"], 1),
                "cost": round(r["cost_score"], 1),
            }
            for r in scored
        },
    }
