"""
Provider Switching Example

Demonstrates how to switch between LLM providers with one line of code.
This is LLMSwap's core feature - zero vendor lock-in.

Before running:
    export ANTHROPIC_API_KEY=sk-ant-...
    export OPENAI_API_KEY=sk-...
"""

from llmswap import LLMClient

def main():
    # Create client
    client = LLMClient(provider="anthropic")
    
    # Query with Anthropic (Claude)
    print("=== Using Anthropic (Claude) ===")
    response1 = client.query("Write a haiku about coding")
    print(response1)
    print(f"Provider: {client.current_provider}\n")
    
    # Switch to OpenAI (GPT)
    client.set_provider("openai")
    
    # Same query, different provider
    print("=== Using OpenAI (GPT) ===")
    response2 = client.query("Write a haiku about coding")
    print(response2)
    print(f"Provider: {client.current_provider}\n")
    
    # Switch to Google (Gemini)
    client.set_provider("gemini")
    
    print("=== Using Google (Gemini) ===")
    response3 = client.query("Write a haiku about coding")
    print(response3)
    print(f"Provider: {client.current_provider}\n")
    
    # The API stays the same - only one line changes!
    print("✅ Same code, 3 different providers - that's LLMSwap!")

if __name__ == "__main__":
    main()
