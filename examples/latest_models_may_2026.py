"""Current model examples - May 2026.

Examples using provider defaults verified for llmswap 5.5.7.

Usage:
    pip install llmswap
    export ANTHROPIC_API_KEY="your-key"
    python latest_models_may_2026.py
"""

from llmswap import LLMClient


def test_claude_sonnet_4():
    """Claude Sonnet 4 - Anthropic balanced production model."""
    print("\n" + "=" * 60)
    print("Claude Sonnet 4")
    print("Anthropic production model | Coding and everyday tasks")
    print("=" * 60)

    client = LLMClient(provider="anthropic", model="claude-sonnet-4-20250514")

    response = client.chat("Write a Python function that finds all prime numbers up to n using the Sieve of Eratosthenes.")
    print(f"\nResponse:\n{response.content}")
    if response.usage:
        print(f"\nTokens: {response.usage}")


def test_claude_opus_41():
    """Claude Opus 4.1 - Anthropic high-capability model."""
    print("\n" + "=" * 60)
    print("Claude Opus 4.1")
    print("Most capable Claude model | Complex reasoning and analysis")
    print("=" * 60)

    client = LLMClient(provider="anthropic", model="claude-opus-4-1-20250805")

    response = client.chat(
        "Summarize the key risks a startup should consider when raising a Series A round."
    )
    print(f"\nResponse:\n{response.content}")
    if response.usage:
        print(f"\nTokens: {response.usage}")


def compare_claude_models():
    """Compare Sonnet 4 vs Opus 4.1 on the same prompt."""
    print("\n" + "=" * 60)
    print("Comparing Claude Sonnet 4 vs Opus 4.1")
    print("=" * 60)

    prompt = "Explain the CAP theorem in two sentences."

    models = [
        ("claude-sonnet-4-20250514", "Sonnet 4 (default, $3/$15 per M tokens)"),
        ("claude-opus-4-1-20250805", "Opus 4.1 (most capable, $15/$75 per M tokens)"),
    ]

    for model_id, label in models:
        print(f"\n--- {label} ---")
        try:
            client = LLMClient(provider="anthropic", model=model_id)
            response = client.chat(prompt)
            print(response.content)
        except Exception as e:
            print(f"Error: {e}")


def test_with_default():
    """Use default provider model from llmswap config."""
    print("\n" + "=" * 60)
    print("Auto-detect with current Anthropic default")
    print("=" * 60)

    client = LLMClient(provider="anthropic")
    response = client.chat("What is dependency injection? Give a Python example.")
    print(f"\nModel used: {client.get_current_model()}")
    print(f"\nResponse:\n{response.content}")


if __name__ == "__main__":
    import os

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY to run these examples.")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    print("llmswap - Current Claude Models (May 2026)")
    print("Models: claude-sonnet-4-20250514 | claude-opus-4-1-20250805")

    test_claude_sonnet_4()
    test_claude_opus_41()
    compare_claude_models()
    test_with_default()

    print("\nDone!")
