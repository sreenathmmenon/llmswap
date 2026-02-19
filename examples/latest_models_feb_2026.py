"""
Latest Models - February 2026
==============================
Examples using the newest models available in llmswap as of February 2026.

New in Feb 2026:
- Claude Sonnet 4.6 (Anthropic) - Feb 17, 2026 - New default
- Claude Opus 4.6 (Anthropic) - Feb 5, 2026 - Most capable

Usage:
    pip install llmswap
    export ANTHROPIC_API_KEY="your-key"
    python latest_models_feb_2026.py
"""

from llmswap import LLMClient


def test_claude_sonnet_46():
    """Claude Sonnet 4.6 - Anthropic's new default model (Feb 17, 2026)"""
    print("\n" + "=" * 60)
    print("Claude Sonnet 4.6 (Released Feb 17, 2026)")
    print("Anthropic's new default | Improved coding & computer use")
    print("=" * 60)

    client = LLMClient(provider="anthropic", model="claude-sonnet-4-6")

    response = client.chat("Write a Python function that finds all prime numbers up to n using the Sieve of Eratosthenes.")
    print(f"\nResponse:\n{response.content}")
    if response.usage:
        print(f"\nTokens: {response.usage}")


def test_claude_opus_46():
    """Claude Opus 4.6 - Anthropic's most capable model (Feb 5, 2026)"""
    print("\n" + "=" * 60)
    print("Claude Opus 4.6 (Released Feb 5, 2026)")
    print("Most capable | Finance Agent benchmark leader | 1M context")
    print("=" * 60)

    client = LLMClient(provider="anthropic", model="claude-opus-4-6")

    response = client.chat(
        "Summarize the key risks a startup should consider when raising a Series A round."
    )
    print(f"\nResponse:\n{response.content}")
    if response.usage:
        print(f"\nTokens: {response.usage}")


def compare_claude_models():
    """Compare Sonnet 4.6 vs Opus 4.6 on the same prompt"""
    print("\n" + "=" * 60)
    print("Comparing Claude Sonnet 4.6 vs Opus 4.6")
    print("=" * 60)

    prompt = "Explain the CAP theorem in two sentences."

    models = [
        ("claude-sonnet-4-6", "Sonnet 4.6 (default, $3/$15 per M tokens)"),
        ("claude-opus-4-6", "Opus 4.6 (most capable, $15/$75 per M tokens)"),
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
    """Use default provider - will pick claude-sonnet-4-6 if ANTHROPIC_API_KEY is set"""
    print("\n" + "=" * 60)
    print("Auto-detect with latest default (claude-sonnet-4-6)")
    print("=" * 60)

    client = LLMClient(provider="anthropic")  # uses claude-sonnet-4-6 by default
    response = client.chat("What is dependency injection? Give a Python example.")
    print(f"\nModel used: {client.get_current_model()}")
    print(f"\nResponse:\n{response.content}")


if __name__ == "__main__":
    import os

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY to run these examples.")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)

    print("llmswap - Latest Claude Models (February 2026)")
    print("Models: claude-sonnet-4-6 | claude-opus-4-6")

    test_claude_sonnet_46()
    test_claude_opus_46()
    compare_claude_models()
    test_with_default()

    print("\nDone!")
