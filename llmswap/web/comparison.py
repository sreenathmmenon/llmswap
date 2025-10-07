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
                results.append({
                    'model': model,
                    'response': None,
                    'error': error_msg,
                    'time': 0,
                    'tokens': 0,
                    'cost': 0
                })

    # Sort results by original model order
    model_order = {model: idx for idx, model in enumerate(models)}
    results.sort(key=lambda x: model_order.get(x['model'], 999))

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
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        # Calculate time
        elapsed = time.time() - start_time

        # Get ACTUAL token counts from API response (if available)
        if hasattr(response, 'usage') and response.usage:
            # Use real token counts from API
            prompt_tokens = response.usage.get('prompt_tokens', 0)
            response_tokens = response.usage.get('completion_tokens', 0) or response.usage.get('output_tokens', 0)
            total_tokens = response.usage.get('total_tokens', prompt_tokens + response_tokens)
        else:
            # Fallback to estimation (rough: ~4 chars per token)
            prompt_tokens = len(prompt) // 4
            response_tokens = len(response_text) // 4
            total_tokens = prompt_tokens + response_tokens

        # Calculate cost with actual token counts
        cost = _estimate_cost(model, prompt_tokens, response_tokens)

        return {
            'model': model,
            'response': response_text,
            'time': round(elapsed, 2),
            'tokens': total_tokens,
            'cost': round(cost, 4)
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
        'openai': 'export OPENAI_API_KEY="your-key-here"',
        'anthropic': 'export ANTHROPIC_API_KEY="your-key-here"',
        'gemini': 'export GEMINI_API_KEY="your-key-here"',
        'xai': 'export XAI_API_KEY="your-key-here"',
        'cohere': 'export COHERE_API_KEY="your-key-here"',
        'perplexity': 'export PERPLEXITY_API_KEY="your-key-here"',
        'watsonx': 'export WATSONX_API_KEY="your-key-here"',
        'groq': 'export GROQ_API_KEY="your-key-here"',
        'ollama': 'Make sure Ollama is running: ollama serve',
    }

    # Check for common error patterns
    if 'API_KEY' in error or 'not found' in error or 'missing' in error.lower():
        provider_name = provider.upper() if provider != 'xai' else 'xAI'
        setup = setup_instructions.get(provider, f'export {provider.upper()}_API_KEY="your-key-here"')

        return f"🔑 {provider_name} API key not configured\n\nTo use {model}:\n{setup}\n\nThen restart the web UI."

    elif 'rate limit' in error.lower():
        return f"⏱️ Rate limit exceeded for {model}\n\nTry again in a few moments or upgrade your API plan."

    elif 'connection' in error.lower() or 'timeout' in error.lower():
        return f"🌐 Connection error for {model}\n\nCheck your internet connection and try again."

    elif 'not running' in error.lower() or 'refused' in error.lower():
        if provider == 'ollama':
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

    if 'gpt' in model_lower or 'o1' in model_lower:
        return 'openai'
    elif 'claude' in model_lower:
        return 'anthropic'
    elif 'gemini' in model_lower:
        return 'gemini'
    elif 'grok' in model_lower:
        return 'xai'
    elif 'command' in model_lower or 'cohere' in model_lower:
        return 'cohere'
    elif 'llama' in model_lower or 'mistral' in model_lower:
        return 'ollama'
    elif 'sonar' in model_lower:
        return 'perplexity'
    elif 'granite' in model_lower:
        return 'watsonx'
    else:
        # Default to openai for unknown models
        return 'openai'


def _estimate_cost(model: str, prompt_tokens: int, response_tokens: int) -> float:
    """
    Estimate cost based on model and token counts.

    Pricing per 1M tokens (as of January 2025):
    - OpenAI: GPT-4o ($2.50/$10), GPT-4o-mini ($0.15/$0.60), GPT-4 ($30/$60)
    - Anthropic: Sonnet 4.5 ($3/$15), Haiku ($1/$5), Opus ($15/$75)
    - Google: Gemini 2.0 Flash ($0.075/$0.30), 1.5 Pro ($1.25/$5.00)
    - xAI: Grok Beta ($5/$15)
    - Perplexity: Sonar Pro ($3/$15)
    - Groq: Free tier (approximated as $0.10/$0.10)
    - Ollama: Local (free)
    """
    pricing = {
        # OpenAI models
        'gpt-4o': (2.50, 10.00),
        'gpt-4o-mini': (0.15, 0.60),
        'gpt-4-turbo': (10, 30),
        'gpt-4': (30, 60),
        'gpt-3.5-turbo': (0.50, 1.50),
        'o1-preview': (15, 60),
        'o1-mini': (3, 12),

        # Anthropic models
        'claude-3-5-sonnet-20241022': (3, 15),
        'claude-3-5-sonnet': (3, 15),
        'claude-3-5-haiku-20241022': (1, 5),
        'claude-3-haiku': (0.25, 1.25),
        'claude-3-opus': (15, 75),
        'claude-3-sonnet': (3, 15),

        # Google models
        'gemini-2.0-flash': (0.075, 0.30),
        'gemini-1.5-flash': (0.075, 0.30),
        'gemini-1.5-pro': (1.25, 5.00),
        'gemini-pro': (0.50, 1.50),

        # xAI models
        'grok-beta': (5, 15),

        # Perplexity models
        'sonar-pro': (3, 15),
        'sonar': (1, 5),

        # Groq (free tier)
        'llama-3.3-70b': (0.10, 0.10),
        'llama': (0.10, 0.10),

        # Ollama (local, free)
        'ollama': (0, 0),
    }

    # Find matching pricing
    input_cost, output_cost = (3, 15)  # Default: Claude Sonnet pricing

    for key, (inp, out) in pricing.items():
        if key in model.lower():
            input_cost, output_cost = inp, out
            break

    # Calculate cost (pricing is per 1M tokens)
    cost = (prompt_tokens * input_cost + response_tokens * output_cost) / 1_000_000

    return cost


def compare_models_streaming(prompt: str, models: List[str], client=None):
    """
    Compare models with streaming responses (generator).

    Yields results as they complete.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if not models or len(models) == 0:
        raise ValueError("Models list cannot be empty")

    if client is None:
        from llmswap import LLMClient
        client = LLMClient()

    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        future_to_model = {
            executor.submit(_query_model, client, model, prompt): model
            for model in models
        }

        for future in as_completed(future_to_model):
            try:
                result = future.result()
                yield result
            except Exception as e:
                model = future_to_model[future]
                yield {
                    'model': model,
                    'response': None,
                    'error': str(e),
                    'time': 0,
                    'tokens': 0,
                    'cost': 0
                }
